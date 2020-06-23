import django_tables2 as tables
import itertools
from django.utils.html import format_html
from django.urls import reverse
from .models import Map


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
        model = Map
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
