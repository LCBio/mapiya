from django.apps import AppConfig


class MapserverConfig(AppConfig):
    name = 'mapserver'

    def ready(self):
        from .models import signals
        from . import plotly
        from . import plotly2
