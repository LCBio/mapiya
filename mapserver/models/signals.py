from django.dispatch import receiver
from django.db.models import signals
from django.core.files.storage import default_storage as storage

import django_rq

from . import Project


@receiver(signals.pre_delete, sender=Project)
def delete_media(**kwargs):
    instance = kwargs.get('instance')
    if storage.exists(instance.media_dir):
        for f in storage.listdir(instance.media_dir)[1]:
            storage.delete(f'{instance.media_dir}/{f}')
        storage.delete(instance.media_dir)


@receiver(signals.post_save, sender=Project)
def project_init_extras(**kwargs):
    if kwargs['created']:
        instance = kwargs.get('instance')
        models_count = instance.atoms.models_count
        instance.info = {
            'models': instance.atoms.models_count,
            'labels': list(instance.atoms.models.keys())
        }

        if models_count < 1:
            instance.error_msg = 'No structures found in uploaded file!'
            instance.status = 'E'
            instance.save(update_fields=['info', 'error_msg', 'status'])

        elif models_count > 50:
            instance.error_msg = 'Too many structures in uploaded file (max 50)!'
            instance.status = 'E'
            instance.save(update_fields=['info', 'error_msg', 'status'])

        else:
            instance.save(update_fields=['info'])
            django_rq.enqueue(instance.create_jobs)
