from django.contrib import admin
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
        return obj.project_set.count()
