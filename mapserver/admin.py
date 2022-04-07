from django.contrib import admin
from . import models
from users.models import User


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = [
        'filename',
        'identity',
        'status',
        'date_init',
        'error_msg'
    ]


@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):

    list_filter = (
        ('project', 'project__identity')
    )

    list_display = [
        'job_id',
        'identity'
    ]

    @admin.display(description='Job')
    def job_id(self, obj):
        return obj

    @admin.display(description='Identity')
    def identity(self, obj):
        return obj.project.identity
