from . import models
import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse
import itertools
import json


# Base class for tables with row numbers
class RowNumberTable(tables.Table):

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
class MapTable(RowNumberTable):

    class Meta:
        model = models.Map
        fields = ('row_number', 'filename')
        attrs = {'class': 'table'}

    filename = tables.Column(
        linkify=True
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
        models_count = json.loads(record.info)['models']
        suffix = f' : {models_count} models' if models_count > 1 else ''
        return f'{record.filename}{suffix}'

    @staticmethod
    def render_buttons(value):
        return format_html(f'''
            <a href="{reverse('map-delete', args=[value])}" data-toggle="modal" data-target="#modal"
               class="text-danger" title="Delete file">
                <i class="fa fa-trash-alt"></i>
            </a>
        ''')


# ngl menu
class NGLTable(tables.Table):

    class Meta:
        attrs = {
            'class': 'table table-borderless table-sm d-none',
            'th': {'class': 'text-white'}
        }
        row_attrs = {
            'id': lambda record: f'rep_{record.pk}'
        }
        # TODO: pagination

    name = tables.Column(
        verbose_name='Name',
        orderable=False
    )

    color = tables.Column(
        verbose_name='Coloring',
        orderable=False
    )

    representation = tables.Column(
        verbose_name='Drawing',
        orderable=False,
    )

    selection = tables.Column(
        verbose_name='Selection',
        orderable=False
    )

    actions = tables.Column(
        attrs={'th': {'class': 'text-center'}},
        orderable=False,
        accessor='pk'
    )

    def __init__(self, **kwargs):
        mapobj = kwargs.pop('mapobj')
        kwargs['data'] = models.Representation.objects.filter(map=mapobj)
        self.base_columns['actions'].verbose_name = format_html(f'''
            <a class="text-success ngl-cmd" href="{reverse('ngl-add', args=[mapobj.pk])}">
                <i class="fas fa-plus-circle"></i>
            </a>
        ''')
        super().__init__(**kwargs)

    @staticmethod
    def render_name(record):
        return format_html(f'''
            <input class="form-control form-control-sm ngl-input" type="text" name="name" value="{record.name}">
        ''')

    @staticmethod
    def render_color(record):
        options = '\n'.join([
            f'<option {"selected" if record.color == color else ""} value="{color.keyword}">{color.name}</option>'
            for color in models.NGLColorScheme.objects.all()
        ])
        return format_html(f'''
            <div class="input-group input-group-sm">
                <select class="custom-select custom-select-sm ngl-input" name="color">{options}</select>
                <div class="input-group-append">
                    <span class="input-group-text">
                        <a class="text-secondary ngl-options" href="{reverse('ngl-options', args=[record.pk])}"
                           data-keyword="color">
                            <i class="fas fa-cog"></i>
                        </a>
                    </span>
                </div>
            </div>
        ''')

    @staticmethod
    def render_representation(record):
        options = '\n'.join([
            f'<option {"selected" if record.representation == rep else ""} value="{rep.keyword}">{rep.name}</option>'
            for rep in models.NGLRepresentation.objects.all()
        ])
        return format_html(f'''
            <div class="input-group input-group-sm">
                <select class="custom-select custom-select-sm ngl-input" name="representation">{options}</select>
                <div class="input-group-append">
                    <span class="input-group-text">
                        <a class="text-secondary ngl-options" href="{reverse('ngl-options', args=[record.pk])}"
                           data-keyword="representation">
                            <i class="fas fa-cog"></i>
                        </a>
                    </span>
                </div>
            </div>
        ''')

    @staticmethod
    def render_selection(record):
        return format_html(f'''
            <div class="input-group input-group-sm">
                <input class="form-control form-control-sm ngl-input" type="text" name="selection"
                       value="{record.selection}">
                <div class="input-group-append">
                    <span class="input-group-text">
                        <a class="text-secondary ngl-options" href="{reverse('ngl-options', args=[record.pk])}"
                           data-keyword="selection">
                            <i class="fas fa-cog"></i>
                        </a>
                    </span>
                </div>
            </div>
        ''')

    @staticmethod
    def render_actions(record):

        eye = f'''
            <a class="text-primary mr-1 ngl-eye" href="javascript:void(0)">
                <i class="fas fa-eye"></i>
            </a>
        '''
        return format_html(f'''
            <div class="d-inline-flex">
                {eye}
                <a class="text-danger ngl-cmd" href="{reverse('ngl-delete', args=[record.pk])}">
                    <i class="fas fa-trash-alt"></i>
                </a>
            </div>
        ''')
