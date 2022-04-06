from crispy_forms import layout, bootstrap
from .tooltips import format_tooltip

HR = layout.HTML('<hr/>')
BR = layout.HTML('<br/>')


class RowField(bootstrap.AppendedText):

    WRAPPER_CLASSES = 'row-field-wrapper'
    CSS_CLASSES = 'form-control-sm custom-select-sm'

    def __init__(self, *args, **kwargs):
        tooltip = format_tooltip(args[0])
        kwargs['wrapper_class'] = f'{kwargs.get("wrapper_class", "")} {self.WRAPPER_CLASSES}'
        kwargs['css_class'] = f'{kwargs.get("css_class", "")} {self.CSS_CLASSES}'
        kwargs['text'] = f'<i class="fas fa-sm fa-question-circle" {tooltip}></i>'
        super().__init__(*args, **kwargs)


class ButtonLink(layout.HTML):

    def __init__(self, href, text, css_class):
        super().__init__(html=f'<a href="{href}" class="{css_class}">{text}</a>')
