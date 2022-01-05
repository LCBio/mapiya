from django.dispatch import receiver
from django.db.models import signals
from django.core.files.storage import default_storage as storage

import django_rq

from . import Project, Job


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
        instance.info = {
            'models': instance.atoms.models_count,
            'labels': list(instance.atoms.models.keys())
        }
        instance.save(update_fields=['info'])

        # TODO: delegate job creation outside of this signal handler,
        #  possibly into queue jobs for larger files

        for model_index in instance.atoms.models:
            job = Job.objects.create(
                project=instance,
                model_index=model_index if model_index else 0,
                status='Q'
            )
            django_rq.enqueue(job.run)
