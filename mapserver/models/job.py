from django.db import models
from django.core.files.base import File, ContentFile
from mollib.atom import Atoms
from mollib.utils import DistanceMatrix
from mapserver.models import Project
from pdbfixer import PDBFixer
from openmm.app import PDBFile
from simtk import unit
import openmm
import numpy as np
import io
import json
import pathlib
import logging
import collections
import subprocess


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
    info = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.QUEUE)
    error = models.TextField(null=True, blank=True)
    logs = models.TextField(null=True, blank=True)
    date_init = models.DateTimeField(auto_now_add=True)

    @property
    def atoms(self):
        return Atoms.from_file(self.pdb.path)

    def get_log(self, key):
        if self.logs:
            try:
                return json.loads(self.logs).get(key)
            except [TypeError, KeyError]:
                pass
        return ''

    def update_log(self, key, log):
        if self.logs:
            try:
                logs = json.loads(self.logs)
            except TypeError:
                logs = {}
        else:
            logs = {}

        logs.update({key: log})
        self.logs = json.dumps(logs)
        self.save(update_fields=['logs'])

    def get_matrix(self):
        atoms = self.atoms.drop('WATER or HYDRO')
        residues = []
        objects = {}
        ix_from = 0
        for chainID, chain in atoms.chains.items():
            protein, other = chain.partition('PROTEIN')
            hetero, nucleic = other.partition('HETERO')

            for obj, type_ in zip([protein, nucleic, hetero], ['protein', 'nucleic', 'hetero']):
                if len(obj):
                    length = len(obj.residues_list)
                    residues.extend(obj.residues_list)
                    objects[type_ + '-' + chainID] = [
                        [f'{r[0].resname}:{r[0].resid}' for r in obj.residues_list],
                        [ix_from, ix_from+length]
                    ]
                    ix_from += length

        distances = np.zeros(shape=(len(residues), len(residues)))
        for i, r1 in enumerate(residues):
            for j, r2 in enumerate(residues[i + 1:], i + 1):
                distances[i, j] = distances[j, i] = np.sqrt(DistanceMatrix(r1.numpy, r2.numpy).d2.min())

        return objects, distances

    def save_matrix(self):
        with io.BytesIO() as f:
            info, matrix = self.get_matrix()
            np.save(f, matrix)
            self.matrix = File(f, name=f'matrix{self.model_index}.npy')

            self.info = json.dumps({
                'labels': info,
                **(json.loads(self.info) if self.info else {})
            })
            self.save(update_fields=['matrix', 'info'])

    def save_pdb(self):
        atoms = self.project.atoms.models[self.model_index] if self.model_index else self.project.atoms
        self.pdb = ContentFile(name=f'model{self.model_index}.pdb', content=atoms.pdb)
        self.save(update_fields=['pdb'])

    def save_results(self, fixer_log, ss_elements, structural_data, hydrogen_bonds):

        # update self.info
        info = json.loads(self.info) if self.info else {}
        info['fixer_log'] = fixer_log
        info['ss_elements'] = ss_elements
        self.info = json.dumps(info)

        # update self.pdb
        path = pathlib.Path(self.pdb.path)
        filename = path.parent / f'{path.stem}_fixed{path.suffix}'
        self.pdb.delete(save=False)
        self.pdb = ContentFile(name=path.name, content=Atoms.from_file(filename).pdb)

        # save additional files
        self.structural_data = ContentFile(name=f'data{self.model_index}.csv', content=structural_data.to_csv())
        self.hydrogen_bonds = ContentFile(name=f'hbonds{self.model_index}.csv', content=hydrogen_bonds.to_csv())

        # commit changes
        self.save()

    def run(self):
        # extract model from uploaded file in self.pdb
        self.save_pdb()

        # run pdb fixer
        self.run_pdbfixer()

        # # run external software and overwrite self.pdb
        # self.save_results(*(external.run_external_software(
        #     self.pdb.path, params=json.loads(self.project.identity.config)
        # )))

        # calculate distance matrix from self.pdb
        self.save_matrix()

    def __str__(self):
        status = dict(self.StatusChoices.choices).get(self.status, 'Unknown')
        return f'{self.project.filename}:{self.model_index} [{status}]'

    def run_pdbfixer(self):

        # setup logging to string
        logger, log = setup_logger('PDBFixer')

        # get config from the Project
        config = self.project.get_config

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
        if config['add_residues'] != 'none':
            fixer.findMissingResidues()
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
                PDBFile.writeFile(fixer.topology, fixer.positions, f)
                self.environment = ContentFile(name=f'environment{self.model_index}.pdb', content=f.getvalue())
                self.save(update_fields=['environment'])
        else:
            logger.info('no solvent or membrane added')

        # Overwrite self.pdb with fixed structure
        with self.pdb.open('wt') as f:
            PDBFile.writeFile(fixer.topology, fixer.positions, f)

        # Save PDBFixer log in the DB
        self.update_log('pdbfixer', log.getvalue())

    def run_pdb2pqr(self):
        pass

    def run_edhb(self):
        pass

    def run_stride(self):
        pass
