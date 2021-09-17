from . import models
from django.dispatch import receiver
from django.db.models import signals
from django.core.files.storage import default_storage as storage
import json


@receiver(signals.pre_delete, sender=models.Map)
def delete_media(**kwargs):
    instance = kwargs.get('instance')
    if storage.exists(instance.media_dir):
        for f in storage.listdir(instance.media_dir)[1]:
            storage.delete(f'{instance.media_dir}/{f}')
        storage.delete(instance.media_dir)


@receiver(signals.post_save, sender=models.Map)
def map_init_extras(**kwargs):
    if kwargs['created']:
        instance = kwargs.get('instance')
        instance.info = json.dumps({
            'models': instance.atoms.models_count,
            'labels': list(instance.atoms.models.keys())
        })
        instance.save(update_fields=['info'])
        for model_number in instance.atoms.models:
            models.MapModel.objects.create(
                map=instance,
                model_number=model_number if model_number else 0
            )
