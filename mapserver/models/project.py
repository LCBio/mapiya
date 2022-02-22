from django.utils.functional import cached_property
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from django.db import models
from django.urls import reverse, reverse_lazy
import django_rq

from mollib.atom import Atoms
from users.models import Identity

from .job import Job


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

    class StatusChoices(models.TextChoices):

        CREATED = 'C'
        PROCESSING = 'P'
        ERROR = 'E'
        FINISHED = 'F'

    ID_LENGTH = 12

    # TODO: Add pdb file validation

    id = models.CharField(max_length=ID_LENGTH, primary_key=True, default=get_map_id)
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    filename = models.CharField(max_length=50)
    pdb = models.FileField(upload_to=pdb_path)
    info = models.JSONField(null=True, blank=True)
    config = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.CREATED)
    date_init = models.DateTimeField(auto_now_add=True)
    error_msg = models.CharField(max_length=255, blank=True, null=True)

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

    def cleanup(self):
        self.info = {}
        self.config = {}
        self.error_msg = None
        self.status = self.StatusChoices.PROCESSING
        self.save()

    def create_jobs(self):
        for model_index in self.atoms.models:
            job = Job.objects.create(
                project=self,
                model_index=model_index if model_index else 0,
                status='Q'
            )
            django_rq.enqueue(job.run)
        self.status = 'P'
        self.save(update_fields=['status'])

    def resubmit_jobs(self):
        self.cleanup()
        self.create_jobs()

    @property
    def progress(self):
        active_link = f'<a href={self.get_absolute_url()}>{self.filename}</a>'
        disabled_link = f'<span class="text-danger temp-label">{self.filename}</span>'
        total_models = self.info.get('models', 0)
        verbose = 'models' if total_models > 1 else 'model'

        error_msg = '<small class="text-danger">{}</small>'
        success_msg = f'<small class="text-success">{total_models} {verbose} ready!</small>'

        init_msg = f'''
            <small class="text-primary progress-label" data-pk="{self.pk}">
                <span>Creating {total_models} {verbose} </span>
                <span class="spinner-grow spinner-grow-sm"></span>
            </small>
        '''
        progress_msg = '''
            <small class="text-info progress-label" data-pk="{}">
                <span>Processing models {}/{} </span>
                <span class="spinner-grow spinner-grow-sm"></span>
            </small>
        '''
        buttons_msg = f'''
            <a href="{reverse_lazy('project-delete', args=[self.pk])}" data-toggle="modal" data-target="#modal"
               class="text-danger" title="Delete file">
                <i class="fa fa-sm fa-trash-alt"></i>
            </a>'''
        resubmit_msg = f'''
            <a href="{reverse_lazy('project-resubmit', args=[self.pk])}"
                class="resubmit-button text-primary" title="Resubmit job">
                 <i class="fa fa-sm fa-redo"></i>
            </a>'''

        completed = True

        if self.status == 'F':
            link = active_link
            msg = success_msg
            buttons_msg = resubmit_msg + buttons_msg

        elif self.status == 'E':
            link = disabled_link
            msg = error_msg.format(self.error_msg)

        elif self.status == 'C':
            link = disabled_link
            msg = init_msg
            completed = False

        else:
            error_jobs = self.job_set.filter(status='E')
            errors = error_jobs.count()
            if errors:
                self.error_msg = ' '.join(error_jobs.values('error'))
                self.status = 'E'
                self.save(update_fields=['status', 'error_msg'])
                return self.progress
            else:
                complete = self.job_set.filter(status='F').count()

                if complete and complete == total_models:
                    self.status = 'F'
                    self.save(update_fields=['status'])
                    return self.progress

                link = active_link if complete else disabled_link
                msg = progress_msg.format(
                    self.pk,
                    complete,
                    total_models
                )
                completed = False
        return {
            'link': format_html(link),
            'msg': format_html(msg),
            'completed': completed,
            'buttons': format_html(buttons_msg)
        }

    def __str__(self):
        return self.filename
