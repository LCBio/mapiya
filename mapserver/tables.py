from . import models
import django_tables2 as tables
import itertools


# Base class for tables with row numbers
class RowNumberTable(tables.Table):

    # TODO: fix row numbers on paginated tables

    row_number = tables.Column(
        verbose_name='#',
        empty_values=(),
        orderable=False
    )

    def __init__(self, *args, **kwargs):
        self.counter = itertools.count(start=1)
        super().__init__(*args, **kwargs)

    def render_row_number(self):
        return '%d' % next(self.counter)


# for the homepage
class ProjectTable(RowNumberTable):

    class Meta:
        model = models.Project
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ('row_number', 'filename', 'progress')
        attrs = {
            'id': 'projectTable',
            'class': 'table table-sm table-borderless table-striped'
        }

    def __init__(self, *args, **kwargs):
        self.TZ = kwargs.pop('TZ', None)
        super().__init__(*args, **kwargs)

    filename = tables.Column(
        verbose_name='Project name'
    )

    progress = tables.Column(
        orderable=False
    )

    buttons = tables.Column(
        verbose_name='',
        orderable=False,
        accessor='pk',
        attrs={
            'td': {'class': 'text-center buttons'},
            'th': {'class': 'text-center'}
        }
    )

    @staticmethod
    def render_filename(record):
        return record.progress.get('link', 'ERROR')

    @staticmethod
    def render_progress(record):
        return record.progress.get('msg', 'ERROR')

    @staticmethod
    def render_buttons(record):
        return record.progress.get('buttons', 'ERROR')