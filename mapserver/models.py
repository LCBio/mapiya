from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib.sessions.models import Session
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from django.urls import reverse
import numpy as np
from mollib.atom import Atoms
from mollib.utils import DistanceMatrix
from .utils import rs8, rs10, rs12


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

    id = models.CharField(max_length=8, primary_key=True, default=rs8)
    email = models.EmailField('email address', unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Identity(models.Model):

    class Meta:
        verbose_name_plural = 'Identities'

    id = models.CharField(
        max_length=10,
        primary_key=True,
        default=rs10
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.OneToOneField(Session, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.id


def pdb_path(instance, filename):
    return f'{instance.identity.id}/{instance.id}.pdb'


@receiver(post_save, sender=Identity)
def clean_orphans(sender, instance, **kwargs):
    if instance.user is None and instance.session is None:
        instance.delete()


class Map(models.Model):

    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=rs12
    )
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    filename = models.CharField(max_length=50)
    pdb = models.FileField(upload_to=pdb_path)

    @property
    def matrixfile(self):
        return f'{self.pdb.path[:-4]}.npy'

    @cached_property
    def atoms(self):
        return Atoms.from_file(self.pdb.path)

    @cached_property
    def calphas(self):
        return self.atoms.select('name CA')

    def save_matrix(self):
        matrix = DistanceMatrix(self.calphas.numpy).distance_map
        np.save(self.matrixfile, matrix)

    @property
    def matrix(self):
        return np.load(self.matrixfile)

    @cached_property
    def labels(self):
        return [f'{atom.resid}:{atom.chain}' for atom in self.calphas]

    @cached_property
    def chains(self):
        return ' '.join([f'{chid}:{len(chain)}' for chid, chain in self.calphas.chains.items()])

    @property
    def jsonify(self):
        return {f'rep{_.pk}': _.jsonify for _ in self.representation_set.all()}

    def get_absolute_url(self):
        return reverse('map-detail', args=[self.id])

    def __str__(self):
        return self.filename


@receiver(pre_delete, sender=Map)
def delete_media(sender, instance, **kwargs):
    instance.pdb.storage.delete(instance.matrixfile)
    instance.pdb.delete()


class NGLColorScheme(models.Model):

    name = models.CharField(max_length=20, unique=True)
    keyword = models.CharField(max_length=20, unique=True)
    help = models.CharField(max_length=100)

    def __str__(self):
        return self.keyword


class NGLRepresentation(models.Model):

    name = models.CharField(max_length=20, unique=True)
    keyword = models.CharField(max_length=20, unique=True)
    options = models.TextField(null=True, blank=True)  # JSON with options, defaults and per option help
    help = models.CharField(max_length=100)

    def __str__(self):
        return self.keyword


class Representation(models.Model):

    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    color = models.ForeignKey(NGLColorScheme, on_delete=models.SET_DEFAULT, default=1)
    representation = models.ForeignKey(NGLRepresentation, on_delete=models.SET_DEFAULT, default=1)
    selection = models.CharField(max_length=200, default='all')
    visible = models.BooleanField(default=True)
    options = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.map.id} - {self.name}'

    @property
    def jsonify(self):
        return {
            'username': self.name,
            'style': self.representation.keyword,
            'colorScheme': self.color.keyword,
            'sele': self.selection
        }


@receiver(post_save, sender=Map)
def create_ngl_representation(**kwargs):
    if kwargs['created']:
        instance = kwargs.get('instance')
        Representation.objects.create(
            map=instance,
            name='Default',
        )
