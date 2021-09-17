from . import models
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.db.models import signals
from django.core.files.storage import default_storage as storage


@receiver(signals.pre_delete, sender=Session)
def clean_orphan_identities(**kwargs):
    instance = kwargs.get('instance')
    if hasattr(instance, 'identity'):
        instance.identity.delete()


@receiver(signals.pre_delete, sender=models.Identity)
def clean_orphan_media(**kwargs):
    instance = kwargs.get('instance')
    if storage.exists(instance.id):
        dirs, files = storage.listdir(instance.id)
        for f in files:
            storage.delete(f'{instance.id}/{f}')
        for d in dirs:
            for f in storage.listdir(f'{instance.id}/{d}')[1]:
                storage.delete(f'{instance.id}/{d}/{f}')
            storage.delete(f'{instance.id}/{d}')
        storage.delete(instance.id)
