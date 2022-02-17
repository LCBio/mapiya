from . import models
import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse
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
        fields = ('row_number', 'filename')
        attrs = {
            'id': 'projectTable',
            'class': 'table table-sm table-striped table-borderless'
        }

    filename = tables.Column()

    progress = tables.Column(
        orderable=False
    )

    buttons = tables.Column(
        verbose_name='',
        orderable=False,
        accessor='pk',
        attrs={
            'td': {'class': 'text-center'},
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
    def render_buttons(value):
        return format_html(f'''
            <a href="{reverse('project-delete', args=[value])}" data-toggle="modal" data-target="#modal"
               class="text-danger" title="Delete file">
                <i class="fa fa-sm fa-trash-alt"></i>
            </a>
        ''')
