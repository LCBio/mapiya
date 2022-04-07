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

