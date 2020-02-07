from django.db import models
from .project import Project, Upload, DataType


class JobType(models.Model):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class JobRecipe(models.Model):

    data_label = models.CharField(max_length=100)
    job_type = models.ForeignKey(JobType, on_delete=models.CASCADE)
    data_type = models.ForeignKey(DataType, on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('data_label', 'job_type')
        ]


class Job(models.Model):

    type = models.ForeignKey(JobType, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class JobData(models.Model):

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    data = models.ForeignKey(Upload, on_delete=models.CASCADE)
    recipe = models.ForeignKey(JobRecipe, on_delete=models.CASCADE)
