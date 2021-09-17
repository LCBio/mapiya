from django.apps import AppConfig
import os


class MapserverConfig(AppConfig):
    name = 'mapserver'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) == 'true':
            from . import signals
            from . import queue
