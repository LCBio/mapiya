from crispy_forms import bootstrap, layout
from . import forms

HR = layout.HTML('<hr/>')
BR = layout.HTML('<br/>')


class RowField(bootstrap.AppendedText):

    TOOLTIPS = {
        'contact_cutoff': {
            'title': 'Contact cutoff',
            'body': 'User sets the value for contact cutoff (the distance between the heavy atoms in different residues) in angstrom [Å].'
                    'The user can later change this value and display contact maps for the changed contact cutoff.',
            'placement': 'left'
        },
        'protonation_ph': {
            'title': 'Protonation pH',
            'body': 'The user sets the value for pH of the modeled environment. The value can range between 0 and 14.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'add_atoms': {
            'title': 'Add atoms',
            'body': 'This option enables users to add missing atoms to the structure.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'add_residues': {
            'title': 'Add residues',
            'body': 'This option enables users to add missing residues to the structure.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'max_loop_length': {
            'title': 'Max loop length',
            'body': 'This option enables users to specify the maximal length of inserted loops.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'keep_heterogens': {
            'title': 'Keep heterogens',
            'body': 'This option enables users to keep heterogeneous atoms from being removed.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'replace_non_standard': {
            'title': 'Replace non-standard amino acids',
            'body': 'This option enables users to replace all non-standard amino acids in the structure for their stand'
                    'ard equivalents.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'apply_mutations': {
            'title': 'Apply mutations',
            'body': 'This option enables users to apply mutations in the structure. The input is in form: three-letter '
                    'amino acid code for an original residue - index of the residue that is being replaced - three-letter'
                    ' amino acid code for a mutated residue : protein chain id. For example VAL-7-ILE:A will mutate val'
                    'ine 7 into isoleucine in chain A.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'add_environment': {
            'title': 'Add environment',
            'body': 'This option enables users to add an environment to a modeled project. The available options are: n'
                    'one, solvent, membrane.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'membrane_position': {
            'title': 'Membrane position',
            'body': 'This option enables users to specify the membrane position. The first number is the position along'
                    ' the Z axis of the center of the membrane and the second number is the the minimal padding distanc'
                    'e between the molecule and the membrane.',
            'icon': 'question-circle',
            'placement': 'left'
        },
    }

    WRAPPER_CLASSES = 'row-field-wrapper'
    CSS_CLASSES = 'form-control-sm custom-select-sm'

    def __init__(self, *args, **kwargs):
        kwargs['wrapper_class'] = f'{kwargs.get("wrapper_class", "")} {self.WRAPPER_CLASSES}'
        kwargs['css_class'] = f'{kwargs.get("css_class", "")} {self.CSS_CLASSES}'
        if args[0] in self.TOOLTIPS:
            kwargs['text'] = f'''<i class="fas fa-question-circle question-help" data-toggle="tooltip" data-placement="right" data-html="true" data-original-title=" {forms.format_tooltip(self.TOOLTIPS[args[0]])['title']} "></i>'''
        else:
            kwargs['text'] = ''
        kwargs['input_size'] = 'input-group-sm'
        super().__init__(*args, **kwargs)


class BoolField(layout.Field):

    template = 'crispy/boolfield.html'


class ButtonLink(layout.HTML):

    def __init__(self, href, text, css_class):
        super().__init__(html=f'<a href="{href}" class="{css_class}">{text}</a>')
