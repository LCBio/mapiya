from django.contrib import admin
from django.db.models import Q
from . import models


@admin.register(models.Identity)
class IdentityAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'user',
        'projects'
    ]

    @admin.display(description='Projects')
    def projects(self, obj):
        total = obj.project_set.count()
        return total
