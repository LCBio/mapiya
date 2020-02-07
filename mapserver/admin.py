from django.contrib import admin
from django.contrib.sessions.models import Session
from .models import User, Identity, Map

admin.site.register([
    Session,
    User,
    Identity,
    Map
])
