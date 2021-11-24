import collections
import io
import logging
import pathlib
import subprocess
import tempfile

import numpy as np
import openmm
import pandas as pd
from django.core.files.base import File, ContentFile
from django.db import models
from openmm.app import PDBFile
from pdbfixer import PDBFixer
from simtk import unit

from mollib.atom import Atoms
from mollib.utils import DistanceMatrix
from . import Project


def compute_path(instance, filename):
    return f'{instance.project.media_dir}/{filename}'


def setup_logger(
        name,
        level=logging.DEBUG,
        fmt='%(asctime)s : %(levelname)s -  %(message)s ',
        date_fmt='%Y/%m/%d %H:%M:%S'
):
    log = io.StringIO()
    logger = logging.getLogger(name)
    log_handler = logging.StreamHandler(log)
    log_handler.setFormatter(fmt=logging.Formatter(fmt=fmt, datefmt=date_fmt))
    logger.addHandler(log_handler)
    logger.setLevel(level)
    return logger, log


class Job(models.Model):

    class StatusChoices(models.TextChoices):

        SUBMITTED = 'S'
        QUEUE = 'Q'
        RUNNING = 'R'
        ERROR = 'E'
        FINISHED = 'F'

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    model_index = models.SmallIntegerField()
    matrix = models.FileField(upload_to=compute_path, null=True, blank=True)
    pdb = models.FileField(upload_to=compute_path, null=True, blank=True)
    environment = models.FileField(upload_to=compute_path, null=True, blank=True)
    structural_data = models.FileField(upload_to=compute_path, null=True, blank=True)
    hydrogen_bonds = models.FileField(upload_to=compute_path, null=True, blank=True)
    pqr = models.FileField(upload_to=compute_path, null=True, blank=True)
    info = models.JSONField(blank=True, default=dict)
    logs = models.JSONField(blank=True, default=dict)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.SUBMITTED)
    error = models.TextField(blank=True, null=True)
    date_init = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = dict(self.StatusChoices.choices).get(self.status, 'Unknown')
        return f'{self.project.filename}:{self.model_index} [{status}]'

    def cleanup(self):
        self.info = {}
        self.logs = {}
        self.error = None
        self.status = self.StatusChoices.QUEUE
        for filename in ['matrix', 'pdb', 'environment', 'structural_data', 'hydrogen_bonds', 'pqr']:
            file = getattr(self, filename)
            if file:
                file.delete(save=False)
        self.save()

    def save_pdb(self):
        atoms = self.project.atoms.models[self.model_index] if self.model_index else self.project.atoms
        self.pdb = ContentFile(name=f'model{self.model_index}.pdb', content=atoms.pdb)

    def run_pdbfixer(self):

        # setup logging to string
        logger, log = setup_logger('PDBFixer')

        # get config from the Project
        config = self.project.config

        # load fixer object from self.pdb
        with self.pdb.open('rt') as f:
            head, tail = self.project.header
            stream = io.StringIO()
            stream.write(''.join([head, f.read(), '\n', tail]))
            stream.seek(0)
            fixer = PDBFixer(pdbfile=stream)

        # Remove heterogens
        if config['keep_heterogens'] == 'water':
            fixer.removeHeterogens(keepWater=True)
            logger.info('Removed heterogens except water')
        elif config['keep_heterogens'] == 'none':
            fixer.removeHeterogens(keepWater=False)
            logger.info('Removed all heterogens including water')
        else:
            logger.info('Kept all heterogens including water')

        # Apply mutations
        if config['apply_mutations']:
            mutations = collections.defaultdict(list)
            for mutation, chain_id in map(
                    lambda x: x.split(':'),
                    config['apply_mutations'].replace(' ', '').split(',')
            ): mutations[chain_id].append(mutation)

            for chain in mutations:
                try:
                    fixer.applyMutations(mutations[chain], chain)
                    logger.info(f'Applied mutations in chain {chain} : {", ".join(mutations[chain])}')
                except:
                    logger.error(f'Invalid mutation in chain {chain} - {", ".join(mutations[chain])}')
        else:
            logger.info('No mutations applied')

        # Replace non-standard residues
        fixer.findNonstandardResidues()
        if config['replace_non_standard']:
            fixer.replaceNonstandardResidues()
            logger.info(f'Replaced non-standard residues: {fixer.nonstandardResidues}')
        else:
            logging.info(f'Non-standard residues were NOT replaced: {fixer.nonstandardResidues}')

        # Rebuild missing residues, the residues actually get added when you call addMissingAtoms()
        fixer.findMissingResidues()
        if config['add_residues'] != 'none':
            fixed_residues = []
            chains = list(fixer.topology.chains())

            # iterate over identified gaps
            for key, residues in dict(fixer.missingResidues).items():
                chain_index, residue_index = key
                chain = chains[chain_index]
                residues_count = len(list(chain.residues()))

                delete_loop = len(residues) < config['max_loop_length']
                delete_internal = config['add_residues'] == 'terminal' and 0 < residue_index < residues_count
                delete_terminal = \
                    config['add_residues'] == 'internal' and (residue_index == 0 or residue_index == residues_count)

                if delete_loop or delete_terminal or delete_internal:
                    del fixer.missingResidues[key]
                else:
                    fixed_residues.extend([f'{chain.id}:{residue_index}:{resname}' for resname in residues])

            if fixed_residues:
                logger.info(f'{len(fixed_residues)} missing residues were rebuilt: {", ".join(fixed_residues)}')
            else:
                logger.info('No residues were missing')
        else:
            logger.info('No missing residues were rebuilt')

        # Add missing atoms
        if config['add_atoms'] not in ['none', 'terminal']:
            fixer.findMissingAtoms()
            if config['add_atoms'] == 'standard':
                fixer.missingTerminals = {}
            elif config['add_atoms'] == 'terminal':
                fixer.missingAtoms = {}

            # inner atoms
            for residue, atoms in fixer.missingAtoms.items():
                for atom in atoms:
                    logger.info(
                        f'{atom.name}-{atom.id} added to {residue.name}-{residue.id} in chain: {residue.chain.id}'
                    )

            # chain terminals
            for residue, terminal in fixer.missingTerminals.items():
                logger.info(f'{terminal} atom added to {residue.name}-{residue.id} in chain: {residue.chain.id}')

            fixer.addMissingAtoms()

        elif config['add_atoms'] == 'none':
            logger.info('No atoms added')

        if config['add_atoms'] in ['hydrogen', 'all']:
            pH = config.get('protonation_ph', 7.0)
            fixer.addMissingHydrogens(pH=pH)
            logger.info(f'Added missing hydrogens for state protonated at pH={pH}')

        # Overwrite self.pdb with fixed structure
        with self.pdb.open('wt') as f:
            PDBFile.writeFile(fixer.topology, fixer.positions, f, keepIds=True)

        # Add a water box
        if config['add_environment'] != 'none':
            ions = [config['positive_ion'], config['negative_ion'], config['ionic_strength']]
            if config['add_environment'] == 'solvent':
                box_size = fixer.topology.getUnitCellDimensions()
                if config['water_box'] == 'unitcell':
                    box_size = box_size
                elif config['water_box'] == 'maxsize':
                    max_size = max(
                        max((pos[i] for pos in fixer.positions)) - min((pos[i] for pos in fixer.positions))
                        for i in range(3)
                    )
                    box_size = max_size * openmm.Vec3(1, 1, 1)
                elif config['water_box'] == 'custom':
                    bs = [float(i) for i in config['box_dimensions'].split(',')]
                    box_size = openmm.Vec3(bs[0], bs[1], bs[2]) * unit.nanometers
                try:
                    fixer.addSolvent(
                        box_size, positiveIon=ions[0], negativeIon=ions[1], ionicStrength=float(ions[2]) * unit.molar
                    )
                    logger.info(
                        f'solvent added: water box dimensions: {box_size}; ion(+): {ions[0]}; ion(-): {ions[1]}; '
                        f'ionic strength: {ions[2]} molar'
                    )
                except Exception as e:
                    logger.warning(f'adding solvent failed due to an error: {e}')

            elif config['add_environment'] == 'membrane':
                mem = [config['lipid_type']]
                mem.extend(config['membrane_position'].split(','))
                try:
                    fixer.addMembrane(lipidType=mem[0], membraneCenterZ=float(mem[1]), minimumPadding=float(mem[2]),
                                      positiveIon=ions[0], negativeIon=ions[1],
                                      ionicStrength=float(ions[2]) * unit.molar)
                    logger.info(
                        f'membrane added: lipid type: {mem[0]}; ion(+): {ions[0]}; ion(-): {ions[1]}; '
                        f'ionic strength: {ions[2]} molar'
                    )

                except Exception as e:
                    logger.warning(f'adding membrane failed due to an error: {e}')

            # save environment file
            with io.StringIO() as f:
                PDBFile.writeFile(fixer.topology, fixer.positions, f, keepIds=True)
                self.environment = ContentFile(name=f'environment{self.model_index}.pdb', content=f.getvalue())
        else:
            logger.info('no solvent or membrane added')

        # Save PDBFixer log in the DB
        self.logs['pdbfixer'] = log.getvalue()

    def compute_matrix(self):
        atoms = Atoms.from_fileobject(self.pdb.open('rt')).drop('WATER or HYDRO')
        residues = []
        info = {}
        ix_from = 0
        for chainID, chain in atoms.chains.items():
            protein, nucleic = chain.partition('PROTEIN or HETERO')

            for obj, type_ in zip([protein, nucleic], ['protein', 'nucleic']):
                if len(obj):
                    length = len(obj.residues_list)
                    residues.extend(obj.residues_list)
                    info[type_ + '-' + chainID] = [
                        [f'{r[0].resname}:{r[0].resid}' for r in obj.residues_list],
                        [ix_from, ix_from + length]
                    ]
                    ix_from += length

        matrix = np.zeros(shape=(len(residues), len(residues)))
        for i, r1 in enumerate(residues):
            for j, r2 in enumerate(residues[i + 1:], i + 1):
                matrix[i, j] = matrix[j, i] = np.sqrt(DistanceMatrix(r1.numpy, r2.numpy).d2.min())

        with io.BytesIO() as f:
            np.save(f, matrix)
            self.matrix = File(f, name=f'matrix{self.model_index}.npy')
            self.info['labels'] = info
            self.status = self.StatusChoices.FINISHED
            self.save()

    def run_apbs(self):
        input_path = pathlib.Path(self.pdb.path)

        with tempfile.TemporaryDirectory(dir='playground') as workdir:
            dir_path = pathlib.Path(workdir)
            apbs_in = dir_path / 'apbs.in'
            pqr_file = dir_path / f'{input_path.stem}.pqr'

            args = ['pdb2pqr', '--ff=PARSE', '--titration-state-method=propka', '--with-ph=7.0',
                    '--apbs-input', apbs_in, input_path, pqr_file]
            proc = subprocess.run(args=args, capture_output=True)
            if not proc.returncode and pqr_file.exists():
                self.pqr = ContentFile(name=f'{pqr_file.name}', content=pqr_file.read_text())
                self.info['apbs'] = apbs_in.read_text()
            self.logs['apbs'] = proc.stderr.decode()

    def run_edhb(self):

        input_path = pathlib.Path(self.pdb.path)

        with tempfile.TemporaryDirectory(dir='playground') as workdir:
            dir_path = pathlib.Path(workdir)
            xls_path = dir_path / 'input.xls'
            args = ['edhb', input_path, '-a', '-B', '-c']
            proc = subprocess.run(args=args, capture_output=True, cwd=dir_path)
            self.logs['edhb'] = proc.stdout.decode(errors='ignore') + proc.stderr.decode(errors='ignore')
            if proc.returncode:
                # TODO: add error handling if no hydrogens present in input pdb
                pass
            else:
                edhb = pd.read_excel(xls_path)
                inds = pd.DataFrame(columns=['chain', 'residue', 'atom', 'ix'])
                with input_path.open('rt') as f:
                    for row in f:
                        if row.startswith('ATOM'):
                            inds.loc[len(inds.index)] = [
                                row[21],
                                row[17:20].strip() + ':' + row[22:26].strip(),
                                row[11:16].strip(),
                                row[4:11].strip()
                            ]

                HB = pd.DataFrame(columns=['chains', 'donor', 'acceptor', 'proton', 'acc_atom', 'ids', 'type', 'bond',
                                           'length', 'angle', 'bifurcation'])

                for index, row in edhb.iterrows():
                    ids = row['atomIDs'].split('-')
                    proton = inds[inds.ix == ids[1]]
                    acceptor = inds[inds.ix == ids[0]]
                    if len(proton) and len(acceptor):  # remove HB with water molecules
                        backbone = ['N', 'H', 'H2', 'H3', 'CA', 'HA', 'C', 'O']
                        chains = proton['chain'].values[0] + ':' + acceptor['chain'].values[0]
                        at_d = proton['atom'].values[0]
                        at_a = acceptor['atom'].values[0]
                        ix_d = proton['ix'].values[0]
                        ix_a = acceptor['ix'].values[0]
                        td = ta = 's'
                        if at_d in backbone:
                            td = 'b'
                        if at_a in backbone:
                            ta = 'b'
                        HB.loc[len(HB.index)] = [chains, proton['residue'].values[0], acceptor['residue'].values[0],
                                                 at_d, at_a, ix_d + ':' + ix_a, td + ta, row['Bond'], row['HB length'],
                                                 row['HB Angle'], row['Bifurcation type']]
                self.hydrogen_bonds = ContentFile(name=f'hbonds{self.model_index}.csv', content=HB.to_csv())

    def run_stride(self):
        args = ['stride', '-h', self.pdb.path]
        proc = subprocess.run(args=args, capture_output=True)

        if proc.returncode:
            # TODO: add error handling for stride
            pass
        else:
            ss_elements = {}
            structural_data = pd.DataFrame(columns=[
                'chain', 'residues', 'secondary_structure', 'solvent_accessibility', 'phi', 'psi', 'mainHB_acceptor'
            ])

            for row in proc.stdout.decode(errors='ignore', encoding='utf-8').split('\n'):
                if row.startswith('LOC'):
                    element = row[5:17].strip()
                    if element not in ss_elements:
                        ss_elements[element] = []
                    ss_elements[element].append(
                        row[18:21].strip() + ':' + row[22:27].strip() + '_' + row[28] + '-' +
                        row[35:38].strip() + ':' + row[41:45].strip() + '_' + row[46])
                elif row.startswith('ASG'):
                    structural_data.loc[len(structural_data.index)] = [
                        row[9],
                        row[5:8].strip() + ':' + row[11:15].strip(),
                        row[24:25].strip(),
                        row[64:69].strip(),
                        row[42:49].strip(),
                        row[52:59].strip(),
                        {}
                    ]
                elif row.startswith('DNR'):
                    acc = row[25:28].strip() + ':' + row[31:35].strip() + '_' + row[29]
                    donor = row[5:8].strip() + ':' + row[11:15].strip()
                    value = [row[41:45].strip(), row[46:52].strip(), row[53:59].strip(), row[60:66].strip(), row[67:73]]
                    structural_data.loc[
                        (structural_data['chain'] == row[9]) & (structural_data['residues'] == donor)
                        ]['mainHB_acceptor'].values[0][acc] = value

            self.logs['stride'] = proc.stderr.decode(encoding='utf-8', errors='ignore')
            self.structural_data = ContentFile(name=f'data{self.model_index}.csv', content=structural_data.to_csv())
            self.info['ss_elements'] = ss_elements

    def run(self):
        self.save_pdb()
        self.run_pdbfixer()
        self.save()
        # self.run_apbs()
        # self.run_stride()
        # self.run_edhb()
        self.compute_matrix()
