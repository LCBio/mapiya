from django.apps import AppConfig


class MapserverConfig(AppConfig):
    name = 'mapserver'

    def ready(self):
        from . import signals
