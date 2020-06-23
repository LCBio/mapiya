import django_tables2 as tables
import itertools
from django.utils.html import format_html
from django.urls import reverse
from . import models


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


class MapTable(RowNumberTable):

    class Meta:
        model = models.Map
        fields = ('row_number', 'filename', 'chains')
        attrs = {'class': 'table table-hover'}

    filename = tables.Column(
        linkify=True
    )

    chains = tables.Column(
        verbose_name='Chains:Residues',
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
    def render_buttons(value):
        return format_html(f'''
            <a href="{reverse('map-delete', args=[value])}" data-toggle="modal" data-target="#modal"
               class="text-danger" title="Delete file">
                <i class="fa fa-trash-alt"></i>
            </a>
        ''')


class NGLTable(tables.Table):

    class Meta:
        attrs = {
            'class': 'table table-borderless table-sm',
            'th': {'class': 'text-white'}
        }

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
            <a class="text-success tablecmd" href="{reverse('map-table', args=[mapobj.pk])}" data-cmd="addrep">
                <i class="fas fa-plus-circle"></i>
            </a>
        ''')
        super().__init__(**kwargs)

    def render_name(self, record):
        return format_html(f'''
            <input class="form-control form-control-sm" type="text" value="{record.name}">
        ''')

    def render_color(self, value):
        options = '\n'.join([
            f'<option {"selected" if value == color else ""} value="{color.keyword}">{color.name}</option>'
            for color in models.NGLColorScheme.objects.all()
        ])
        return format_html(f'''
            <select class="custom-select custom-select-sm">{options}</select>
        ''')

    def render_representation(self, value):
        options = '\n'.join([
            f'<option {"selected" if value == rep else ""} value="{rep.keyword}">{rep.name}</option>'
            for rep in models.NGLRepresentation.objects.all()
        ])
        return format_html(f'''
            <div class="input-group input-group-sm">
                <select class="custom-select custom-select-sm">{options}</select>
                <div class="input-group-append">
                    <span class="input-group-text">
                        <a class="text-secondary" href="#">
                            <i class="fas fa-cog"></i>
                        </a>
                    </span>
                </div>
            </div>
        ''')

    def render_selection(self, value):
        return format_html(f'''
            <div class="input-group input-group-sm">
                <input class="form-control form-control-sm" type="text" value="{value}">
                <div class="input-group-append">
                    <span class="input-group-text">
                        <a class="text-secondary" href="#"><i class="fas fa-cog"></i></a>
                    </span>
                </div>
            </div>
        ''')

    def render_actions(self, record):
        href = reverse('map-table', args=[record.map.pk])

        eye = f'''
            <a class="text-primary mr-1 tablecmd" href="{href}" data-cmd="update" data-pk="{record.pk}">
                <i class="fas fa-eye{"" if record.visible else "-slash"}"></i>
            </a>
        '''
        return format_html(f'''
            <div class="d-inline-flex">
                {eye}
                <a class="text-danger tablecmd" href="{href}" data-cmd="delrep" data-pk="{record.pk}">
                    <i class="fas fa-trash-alt"></i>
                </a>
            </div>
        ''')
