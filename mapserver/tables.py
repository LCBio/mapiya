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
        complete, total = record.progress
        html = f'<a href={record.get_absolute_url()}>{record.filename}</a>' if complete else \
            f'<span class="text-danger temp-label">{record.filename}</span>'
        return format_html(html)

    @staticmethod
    def render_progress(record):
        complete, total = record.progress
        verbose = 'models' if total > 1 else 'model'
        html = f'<small class="text-success">{total} {verbose} ready!</small>' \
            if complete == total else \
            f'''
                <small class="text-danger progress-label" data-pk="{record.pk}">
                    Processing models <span class="complete-entry">{complete}</span>/{total}
                    <span class="spinner-grow spinner-grow-sm text-danger"></span>
                </small>
            '''
        return format_html(html)

    @staticmethod
    def render_buttons(value):
        return format_html(f'''
            <a href="{reverse('project-delete', args=[value])}" data-toggle="modal" data-target="#modal"
               class="text-danger" title="Delete file">
                <i class="fa fa-sm fa-trash-alt"></i>
            </a>
        ''')
