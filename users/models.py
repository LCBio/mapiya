from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.sessions.models import Session
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password, **kwargs):

        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **kwargs):

        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField('email address', unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


def get_identity_id():
    while True:
        id = get_random_string(length=Identity.ID_LENGTH)
        try:
            Identity.objects.get(id=id)
        except Identity.DoesNotExist:
            return id


class Identity(models.Model):

    ID_LENGTH = 10

    class Meta:
        verbose_name_plural = 'Identities'

    id = models.CharField(max_length=ID_LENGTH, primary_key=True, default=get_identity_id)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.OneToOneField(Session, on_delete=models.SET_NULL, null=True, blank=True)
    config = models.JSONField(null=True, blank=True)
    # TODO: limit number of running jobs per user

    def __str__(self):
        return self.id
