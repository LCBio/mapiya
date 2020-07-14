from django.contrib import admin
from django.contrib.sessions.models import Session
from . import models

admin.site.register([
    Session,
    models.User,
    models.Identity,
    models.Map,
    models.NGLColorScheme,
    models.NGLRepresentation,
    models.Representation,
])
