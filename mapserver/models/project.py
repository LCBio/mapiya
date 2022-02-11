import json
import io

from django.utils.functional import cached_property
from django.utils.crypto import get_random_string
from django.db import models
from django.urls import reverse

from mollib.atom import Atoms
from users.models import Identity


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
    info = models.JSONField(null=True, blank=True)
    config = models.JSONField(null=True, blank=True)

    @property
    def media_dir(self):
        return f'{self.identity.id}/{self.id}'

    @cached_property
    def atoms(self):
        return Atoms.from_fileobject(self.pdb.open('rt'))

    @cached_property
    def header(self):
        head, tail = [], []
        with self.pdb.open('rt') as f:
            for line in f:
                if not any(map(lambda x: line.startswith(x), ['MODEL', 'ENDMDL', 'ATOM', 'HETATM', 'TER', 'ANISOU'])):
                    if any(map(lambda x: line.startswith(x), ['CONECT', 'MASTER', 'END'])):
                        tail.append(line)
                    else:
                        head.append(line)
        return ''.join(head), ''.join(tail)

    @property
    def progress(self):
        total = self.job_set.count()
        incomplete = self.job_set.exclude(status='F').count()
        return total - incomplete, total

    @property
    def error(self):
        return self.job_set.filter(status='E').count() > 0

    def get_absolute_url(self):
        return reverse('project-detail', args=[self.id])

    @property
    def molstar_url(self):
        return reverse('project-molstar', args=[self.pk])

    @property
    def fixed_pdb(self):
        completed_jobs = self.job_set.filter(status='F')
        pdb = []
        for job in completed_jobs:
            pdb.append(f'MODEL{job.model_index:9d}\n')
            for line in job.pdb.open('rt').readlines():
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    pdb.append(line)
            pdb.append('ENDMDL\n')
        return ''.join(pdb)

    @property
    def data(self):
        return {
            'filename': self.filename,
            'config': self.config,
            'jobs': [{
                'index': job.model_index,
                'status': job.status
            } for job in self.job_set.all()]
        }

    def __str__(self):
        return self.filename
