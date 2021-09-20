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
class MapTable(RowNumberTable):

    class Meta:
        model = models.Map
        fields = ('row_number', 'filename')
        attrs = {'class': 'table table-sm table-striped table-borderless'}

    filename = tables.Column(
        accessor='pk'
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
    def render_filename(value):
        current_map = models.Map.objects.get(pk=value)
        if current_map.mapmodel_set.exclude(status='F').exists():
            html = f'''
                <div class="disabled-link text-danger" data-pk="{current_map.pk}">
                    {current_map}
                    <span class="small">In progress ...</span>
                    <div class="spinner-grow spinner-grow-sm" role="status"></div>
                </div>
            '''
        else:
            html = f'<a href="{current_map.get_absolute_url()}">{current_map}</a>'
        return format_html(html)

    @staticmethod
    def render_buttons(value):
        return format_html(f'''
            <a href="{reverse('map-delete', args=[value])}" data-toggle="modal" data-target="#modal"
               class="text-danger" title="Delete file">
                <i class="fa fa-sm fa-trash-alt"></i>
            </a>
        ''')
