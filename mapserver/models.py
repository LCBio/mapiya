from django.utils.functional import cached_property
from django.utils.crypto import get_random_string
from django.db import models
from django.core.files import File
from django.urls import reverse
from mollib.atom import Atoms
from mollib.utils import DistanceMatrix
from users.models import Identity
import numpy as np
import io
import json


def project_pdb_path(instance, filename):
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
    pdb = models.FileField(upload_to=project_pdb_path)
    info = models.TextField(null=True, blank=True)

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

    def get_matrix(self, model_number):
        model = self.atoms.models[model_number] if model_number else self.atoms
        atoms = model.drop('WATER or HYDRO')
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

        return json.dumps(objects), distances

    def get_absolute_url(self):
        return reverse('project-detail', args=[self.id])

    def __str__(self):
        return self.filename


def matrix_path(instance, filename):
    return f'{instance.project.media_dir}/{filename}'


class Job(models.Model):

    class StatusChoices(models.TextChoices):

        QUEUE = 'Q'
        RUNNING = 'R'
        ERROR = 'E'
        FINISHED = 'F'

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    model_number = models.SmallIntegerField()
    matrix = models.FileField(upload_to=matrix_path, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.QUEUE)
    date_init = models.DateTimeField(auto_now_add=True)

    def save_matrix(self):
        with io.BytesIO() as f:
            info, matrix = self.project.get_matrix(self.model_number)
            np.save(f, matrix)
            self.matrix = File(f, name=f'matrix{self.model_number}.npy')
            self.info = info
            self.save(update_fields=['matrix', 'info'])

    def __str__(self):
        status = dict(self.StatusChoices.choices).get(self.status, 'Unknown')
        return f'{self.project.filename}:{self.model_number} [{status}]'
