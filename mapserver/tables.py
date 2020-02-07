import django_tables2 as tables
import itertools
from django.utils.html import format_html
from .models import Map


# Base class for tables with row numbers
class RowNumberTable(tables.Table):

    row_number = tables.Column(
        verbose_name='Nr',
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
        template_name = 'mapserver/table.html'
        attrs = {'class': 'table table-hover'}

    filename = tables.Column(
        linkify=True
    )

    chains = tables.Column(
        verbose_name='Chains:Residues'
    )

    buttons = tables.Column(
        verbose_name='Delete',
        accessor='pk',
        attrs={
            'td': {'class': 'text-center'},
            'th': {'class': 'text-center'}
        }
    )

    @staticmethod
    def render_buttons(value):
        return format_html('''
            <a href="#" class="text-danger"><i class="fa fa-trash"></i></a>
        ''')
