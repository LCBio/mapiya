import pandas
from django.utils.functional import cached_property
from django.utils.crypto import get_random_string
from django.db import models
from django.core.files.base import File, ContentFile
from django.urls import reverse
from mollib.atom import Atoms
from mollib.utils import DistanceMatrix
from users.models import Identity
from . import external
import numpy as np
import io
import json
import pathlib


def pdb_path(instance, filename):
    suffix = '' if filename.endswith('.pdb') else '.pdb'
    return f'{instance.media_dir}/{filename}{suffix}'


def get_map_id():
    while True:
        map_id = get_random_string(Project.ID_LENGTH)
        try:
            Project.objects.get(id=map_id)
        except Project.DoesNotExist:
            return map_id


class Project(models.Model):

    ID_LENGTH = 12

    # TODO: Add pdb file validation

    id = models.CharField(max_length=ID_LENGTH, primary_key=True, default=get_map_id)
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    filename = models.CharField(max_length=50)
    pdb = models.FileField(upload_to=pdb_path)
    info = models.TextField(null=True, blank=True)
    config = models.TextField(null=True, blank=True)

    @property
    def media_dir(self):
        return f'{self.identity.id}/{self.id}'

    @cached_property
    def atoms(self):
        return Atoms.from_fileobject(self.pdb.open('rt'))

    @property
    def progress(self):
        total = self.job_set.count()
        incomplete = self.job_set.exclude(status='F').count()
        return total - incomplete, total

    def get_absolute_url(self):
        return reverse('project-detail', args=[self.id])

    def __str__(self):
        return self.filename


def compute_path(instance, filename):
    return f'{instance.project.media_dir}/{filename}'


class Job(models.Model):

    class StatusChoices(models.TextChoices):

        QUEUE = 'Q'
        RUNNING = 'R'
        ERROR = 'E'
        FINISHED = 'F'

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    model_number = models.SmallIntegerField()
    matrix = models.FileField(upload_to=compute_path, null=True, blank=True)
    pdb = models.FileField(upload_to=compute_path, null=True, blank=True)
    structural_data = models.FileField(upload_to=compute_path, null=True, blank=True)
    hydrogen_bonds = models.FileField(upload_to=compute_path, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.QUEUE)
    date_init = models.DateTimeField(auto_now_add=True)

    @property
    def atoms(self):
        return Atoms.from_file(self.pdb.path)

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
            self.matrix = File(f, name=f'matrix{self.model_number}.npy')
            info.update(json.loads(self.info) if self.info else {})
            self.info = json.dumps(info)
            self.save(update_fields=['matrix', 'info'])

    def save_pdb(self):
        atoms = self.project.atoms.models[self.model_number] if self.model_number else self.project.atoms
        self.pdb = ContentFile(name=f'model{self.model_number}.pdb', content=atoms.pdb)
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
        self.structural_data = ContentFile(name='data.csv', content=structural_data.to_csv())
        self.hydrogen_bonds = ContentFile(name='hbonds.csv', content=hydrogen_bonds.to_csv())

        # commit changes
        self.save()

    def run(self):
        # extract model from uploaded file in self.pdb
        self.save_pdb()

        # run external software and overwrite self.pdb
        self.save_results(*(external.run_external_software(
            self.pdb.path, params=json.loads(self.project.identity.config)
        )))

        # calculate distance matrix from self.pdb
        self.save_matrix()

    def __str__(self):
        status = dict(self.StatusChoices.choices).get(self.status, 'Unknown')
        return f'{self.project.filename}:{self.model_number} [{status}]'
