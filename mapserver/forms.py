import json

from django import forms
from django.urls import reverse
from crispy_forms import layout, helper, bootstrap
from users.forms import CrispyFormMixin
from . import layouts


class RCSBForm(CrispyFormMixin, forms.Form):

    code = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter 4-letter PDB code (i.e. 2gb1).'}
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.form_action = reverse('rcsb')
        self.helper.form_id = 'rcsbForm'
        self.helper.layout = layout.Layout(
            'code',
            layout.HTML(f'''<button type="submit" class="btn btn-success btn-block mty-3">Submit</button>'''),
        )


def format_tooltip(tooltip):

    html = f'''
        <h5>
            {tooltip.get('title', 'Example tooltip title')}
            <i class="fas fa-{tooltip.get('icon')}"></i>
        </h5>
        <hr/>
        <small>{tooltip.get('body', 'Tooltip body missing')}</small>
    '''

    return {
        'data-toggle': 'tooltip',
        'data-placement': tooltip.get('placement', 'left'),
        'data-html': 'true',
        'title': html
    }


class OptionsForm(forms.Form):

    TOOLTIPS = {
        'contact_cutoff': {
            'title': 'Contact cutoff',
            'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labor'
                    'e et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi '
                    'ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse'
                    ' cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in c'
                    'ulpa qui officia deserunt mollit anim id est laborum.',
            'icon': 'question-circle',
            'placement': 'left'
        }
    }

    HELP_TEXT = {
        'protonation_ph': 'Example help text'
    }

    DEFAULTS = {
        'contact_cutoff': 8.0,
        'protonation_ph': 7.0,
        'add_atoms': 'none',
        'add_residues': 'none',
        'max_loop_length': 5,
        'keep_heterogens': 'none',
        'replace_non_standard': False,
        'apply_mutations': '',
        'add_environment': 'none',
        'positive_ion': 'Na+',
        'negative_ion': 'Cl-',
        'ionic_strength': 1.0,
        'water_box': 'unit cell',
        'box_dimensions': '5, 5, 5',
        'lipid_type': 'POPC',
        'membrane_position': '0, 1',
        'hydrogen_bonds': False,
        'secondary_structure': False
    }

    contact_cutoff = forms.FloatField(
        min_value=0,
        max_value=20.0,
        widget=forms.NumberInput(attrs={'step': 0.1}),
        label='contact cutoff [&#8491;]',
    )

    protonation_ph = forms.FloatField(
        min_value=0,
        max_value=14.0,
        widget=forms.NumberInput(attrs={
            'step': 0.1,
        }),
        label='protonation pH',
    )

    add_atoms = forms.ChoiceField(
        choices=[
            ('all', 'all'),
            ('heavy', 'heavy'),
            ('standard', 'standard'),
            ('terminal', 'terminal'),
            ('hydrogen', 'hydrogen'),
            ('none', 'none')
        ],
        label='add atoms'
    )

    add_residues = forms.ChoiceField(
        choices=[
            ('all', 'all'),
            ('internal', 'internal'),
            ('terminal', 'terminal'),
            ('none', 'none'),
        ],
        label='add residues'
    )

    max_loop_length = forms.IntegerField(
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'data-requirements': json.dumps({'add_residues': ['all', 'internal', 'terminal']})
        }),
        label='&#8627; max loop length',
    )

    keep_heterogens = forms.ChoiceField(
        choices=[
            ('all', 'all'),
            ('water', 'water'),
            ('none', 'none')
        ],
        label='keep heterogens'
    )

    replace_non_standard = forms.ChoiceField(
        choices=[(False, 'no'), (True, 'yes')],
        label='replace non-standard aa'
    )

    apply_mutations = forms.CharField(
        required=False,
        label='apply mutations',
        widget=forms.TextInput(attrs={'placeholder': 'e.g., VAL-3-ILE:A, ILE-7-VAL:A'})
    )

    add_environment = forms.ChoiceField(
        choices=[
            ('solvent', 'solvent'),
            ('membrane', 'membrane'),
            ('none', 'none')
        ],
        label='add environment'
    )

    positive_ion = forms.ChoiceField(
        choices=[
            ('Na+', 'Na+'),
            ('Cs+', 'Cs+'),
            ('K+', 'K+'),
            ('Li+', 'Li+'),
            ('Rb+', 'Rb+'),
        ],
        widget=forms.Select(attrs={
            'data-requirements': json.dumps({'add_environment': ['solvent', 'membrane']})
        }),
        label='&#8627; positive ion',
    )

    negative_ion = forms.ChoiceField(
        choices=[
            ('Cl-', 'Cl-'),
            ('Br-', 'Br-'),
            ('F-', 'F-'),
            ('I-', 'I-'),
        ],
        widget=forms.Select(attrs={
            'data-requirements': json.dumps({'add_environment': ['solvent', 'membrane']})
        }),
        label='&#8627; negative ion',
    )

    ionic_strength = forms.FloatField(
        min_value=0,
        max_value=1,
        widget=forms.NumberInput(attrs={
            'step': 0.01,
            'data-requirements': json.dumps({'add_environment': ['solvent', 'membrane']})
        }),
        label='&#8627; ionic strength',
    )

    water_box = forms.ChoiceField(
        choices=[
            ('unit cell', 'unit cell'),
            ('max size', 'max size'),
            ('custom', 'custom'),
        ],
        widget=forms.Select(attrs={
            'data-requirements': json.dumps({'add_environment': ['solvent']})
        }),
        label='&#8627; water box',
    )

    box_dimensions = forms.CharField(
        # TODO: change to triple input field WxHxD
        widget=forms.TextInput(attrs={
            'placeholder': '5,5,5',
            'data-requirements': json.dumps({
                'add_environment': ['solvent'],
                'water_box': ['custom']
            })
        }),
        label='&bull; &#8627; box dimensions'
    )

    lipid_type = forms.ChoiceField(
        choices=[
            ('POPC', 'POPC'),
            ('POPE', 'POPE'),
            ('DLPC', 'DLPC'),
            ('DLPE', 'DLPE'),
            ('DMPC', 'DMPC'),
            ('DOPC', 'DOPC'),
            ('DPPC', 'DPPC')
        ],
        widget=forms.Select(attrs={
            'data-requirements': json.dumps({'add_environment': ['membrane']})
        }),
        label='&#8627; lipid type',
    )

    membrane_position = forms.CharField(
        widget=forms.TextInput(attrs={
            'data-requirements': json.dumps({'add_environment': ['membrane']})
        }),
        label='&#8627; membrane position',
    )

    hydrogen_bonds = forms.BooleanField(
        required=False,
        label='Calculate hydrogen bonds'
    )

    secondary_structure = forms.BooleanField(
        required=False,
        label='Calculate secondary structure'
    )

    electrostatics = forms.BooleanField(
        required=False,
        label='Calculate electrostatics'
    )

    def clean_replace_non_standard(self):
        return self.cleaned_data['replace_non_standard'] in ['True', 'true', True]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, help_text in self.HELP_TEXT.items():
            self.fields[field_name].help_text = help_text

        for field_name, tooltip in self.TOOLTIPS.items():
            self.fields[field_name].widget.attrs.update(format_tooltip(tooltip))

        self.helper = helper.FormHelper()
        self.helper.form_show_errors = True
        self.helper.form_show_labels = True
        self.helper.use_custom_control = True
        self.helper.form_tag = True
        self.helper.form_action = reverse('update-options')
        self.helper.form_method = 'post'
        self.helper.form_id = 'optionsForm'
        self.helper.label_class = 'col-4 small'
        self.helper.field_class = 'col-8'

        pdbfixer_layout = layout.Column(
            layouts.RowField('add_atoms'),
            layouts.RowField('add_residues'),
            layouts.RowField('max_loop_length'),
            layouts.RowField('keep_heterogens'),
            layouts.RowField('replace_non_standard'),
            layouts.RowField('apply_mutations'),
            layouts.RowField('add_environment'),
            layouts.RowField('positive_ion'),
            layouts.RowField('negative_ion'),
            layouts.RowField('ionic_strength'),
            layouts.RowField('water_box'),
            layouts.RowField('box_dimensions'),
            layouts.RowField('lipid_type'),
            layouts.RowField('membrane_position'),
        )

        options_layout = layout.Column(
            layouts.RowField('contact_cutoff'),
            layouts.RowField('protonation_ph'),
            layouts.BoolField('hydrogen_bonds'),
            layouts.BoolField('secondary_structure'),
            layouts.BoolField('electrostatics'),
        )

        submit_button = layouts.ButtonLink(
            href=reverse('reset-options'),
            text='Reset to defaults',
            css_class='btn btn-danger btn-block'
        )

        tab1header = 'General options'
        tab2Header = 'Fix structure with PDBfixer'

        nav_layout = layout.HTML(f'''
        <ul class="nav nav-tabs" id="myTab" role="tablist">
          <li class="nav-item" role="presentation">
            <a class="nav-link active" id="home-tab" data-toggle="tab" href="#home" role="tab">{tab1header}</a>
          </li>
          <li class="nav-item" role="presentation">
            <a class="nav-link" id="profile-tab" data-toggle="tab" href="#profile" role="tab">{tab2Header}</a>
          </li>
        </ul>
        ''')

        tabs_layout = layout.Div(
            layout.Div(
                options_layout,
                css_class='tab-pane fade show active',
                css_id='home',
                role='tabpanel'
            ),
            layout.Div(
                pdbfixer_layout,
                css_class='tab-pane fade',
                css_id='profile',
                role='tabpanel'
            ),
            css_class='tab-content',
            css_id='myTabContent'
        )

        self.helper.layout = layout.Div(
            nav_layout,
            tabs_layout,
            submit_button
        )
