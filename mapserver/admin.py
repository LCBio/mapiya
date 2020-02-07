from django.contrib import admin
from django.contrib.sessions.models import Session
from mapserver import models

admin.site.register([
    Session,
    models.UserSession,
    models.Identity,
    models.Project,
    models.DataType,
    models.Upload,
    models.JobType,
    models.JobRecipe,
    models.Job,
    models.JobData,
])