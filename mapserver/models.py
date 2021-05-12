from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib.sessions.models import Session
from django.db import models
from django.core.files import File
from django.urls import reverse
from mollib.atom import Atoms
from mollib.utils import DistanceMatrix
from .utils import rs8, rs10, rs12
import numpy as np
import io
import json


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
    suffix = '' if filename.endswith('.pdb') else '.pdb'
    return f'{instance.media_dir}/{filename}{suffix}'


class Map(models.Model):

    # TODO: Add pdb file validation

    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=rs12
    )
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE)
    filename = models.CharField(max_length=50)
    pdb = models.FileField(upload_to=pdb_path)
    info = models.TextField(null=True, blank=True)

    @property
    def media_dir(self):
        return f'{self.identity.id}/{self.id}'

    @cached_property
    def atoms(self):
        return Atoms.from_fileobject(self.pdb.open('rt'))

    def get_matrix(self, model=0):
        atoms = self.atoms.models_list[model].drop('WATER or HYDRO')
        residues = []
        objects = {}
        ix_from = 0
        for chainID, chain in atoms.chains.items():
            protein, other = chain.partition('PROTEIN')
            hetero, nucleic = other.partition('HETERO')

            for obj, type_ in zip([protein, nucleic, hetero], ['protein', 'nucleic', 'hetero']):
                if len(obj):
                    length = len(obj.residues_list)
                    residues.extend(obj.residues_list)
                    objects[type_+'-'+chainID] = [[f'{r[0].resname}:{r[0].resid}' for r in obj.residues_list],[ix_from, ix_from+length-1]]
                    ix_from += length

        distances = np.zeros(shape=(len(residues), len(residues)))
        for i, r1 in enumerate(residues):
            for j, r2 in enumerate(residues[i + 1:], i + 1):
                distances[i, j] = distances[j, i] = np.sqrt(DistanceMatrix(r1.numpy, r2.numpy).d2.min())

        return json.dumps(objects), distances

    def save_matrix(self, model=0):
        with io.BytesIO() as f:
            info, matrix = self.get_matrix(model)
            np.save(f, matrix)
            MapModel.objects.create(
                map=self,
                matrix=File(f, name=f'matrix{model}.npy'),
                info=info,
                number=model
            )

    def get_absolute_url(self):
        return reverse('map-detail', args=[self.id])

    def __str__(self):
        return self.filename


def matrix_path(instance, filename):
    return f'{instance.map.media_dir}/{filename}'


class MapModel(models.Model):

    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    number = models.SmallIntegerField()
    matrix = models.FileField(upload_to=matrix_path, null=True, blank=True)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.map.filename} - {self.number}'


class NGLColorScheme(models.Model):

    name = models.CharField(max_length=20, unique=True)
    keyword = models.CharField(max_length=20, unique=True)
    options = models.TextField(null=True, blank=True)
    help = models.CharField(max_length=100)

    def __str__(self):
        return self.keyword


class NGLRepresentation(models.Model):

    name = models.CharField(max_length=20, unique=True)
    keyword = models.CharField(max_length=20, unique=True)
    options = models.TextField(null=True, blank=True)
    help = models.CharField(max_length=100)

    def __str__(self):
        return self.keyword


class Representation(models.Model):

    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    color = models.ForeignKey(NGLColorScheme, on_delete=models.SET_DEFAULT, default=1)
    representation = models.ForeignKey(NGLRepresentation, on_delete=models.SET_DEFAULT, default=1)
    selection = models.CharField(max_length=200, default='all')
    options = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.map.id} - {self.name}'
