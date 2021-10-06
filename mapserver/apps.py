from django.apps import AppConfig
import os


class MapserverConfig(AppConfig):
    name = 'mapserver'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) == 'true':
            from .models import signals
            from . import queue
            from . import plotly
