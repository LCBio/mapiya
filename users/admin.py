from django.contrib import admin
from . import models

admin.site.register([
    models.User,
    models.Identity,
    models.Session
])
