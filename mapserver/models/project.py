from django.db import models
from django.urls import reverse
from .identity import Identity


class Project(models.Model):

    owner = models.ForeignKey(Identity, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default='New Project')

    def __str__(self):
        return self.name


class DataType(models.Model):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


def compute_dir(instance, filename):
    return f'{instance.project.owner_id}/{instance.project.id}/{filename}'


class Upload(models.Model):

    type = models.ForeignKey(DataType, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to=compute_dir)

    def get_absolute_url(self):
        return reverse('upload-detail', args=[self.pk])

    def __str__(self):
        return self.file.url
