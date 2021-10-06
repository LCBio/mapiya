from django.db import models
from django.core.files.base import File, ContentFile
from mollib.atom import Atoms
from mollib.utils import DistanceMatrix
from mapserver.models import Project
from pdbfixer import PDBFixer
from openmm.app import PDBFile
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
            fixer = PDBFixer(pdbfile=f)

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
                    config['specify_mutations'].replace(' ', '').split(',')
            ): mutations[chain_id].append(mutation)

            for chain in mutations:
                try:
                    fixer.applyMutations(mutations[chain], chain)
                    logger.info(f'Applied mutations in chain {chain} : {", ".join(mutations[chain])}.')
                except:
                    logger.error(f'Invalid mutation in chain {chain} - {", ".join(mutations[chain])}.')
        else:
            logger.info('No mutations applied.')

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
            for key, residues in fixer.missingResidues.items():
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
                logger.info('No residues were missing.')
        else:
            logger.info('No missing residues were rebuilt.')

        # Save PDBFixer log in the DB
        self.update_log('pdbfixer', log.getvalue())

        # Overwrite self.pdb with fixed structure
        with self.pdb.open('wt') as f:
            PDBFile.writeFile(fixer.topology, fixer.positions, f)

    def run_pdb2pqr(self):
        pass

    def run_edhb(self):
        pass

    def run_stride(self):
        pass
