from crispy_forms import layout

HR = layout.HTML('<hr/>')
BR = layout.HTML('<br/>')


class RowField(layout.Field):

    WRAPPER_CLASSES = 'd-flex justify-content-start align-items-baseline'
    CSS_CLASSES = 'form-control-sm custom-select-sm'

    def __init__(self, *args, **kwargs):
        kwargs['wrapper_class'] = f'{kwargs.get("wrapper_class", "")} {self.WRAPPER_CLASSES}'
        kwargs['css_class'] = f'{kwargs.get("css_class", "")} {self.CSS_CLASSES}'
        super().__init__(*args, **kwargs)


class BoolField(layout.Field):

    template = 'crispy/boolfield.html'


class ButtonLink(layout.HTML):

    def __init__(self, href, text, css_class):
        super().__init__(html=f'<a href="{href}" class="{css_class}">{text}</a>')
