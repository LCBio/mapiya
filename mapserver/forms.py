import json

from django import forms
from django.urls import reverse
from crispy_forms import layout, helper
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
            'body': 'User sets the value for contact cutoff (in angstrom [Å]). The distance between the two closest '
                    'heavy atoms in two different residues is considered contact if it is below the contact cutoff '
                    'value. In the project view for a particular file, the user can later change this value and display'
                    ' contact maps for the changed contact cutoff.',
            'placement': 'left'
        },
        'protonation_ph': {
            'title': 'Protonation pH',
            'body': 'The user sets the value for pH of the modeled environment. The value can range between 0 and 14.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'hydrogen_bonds': {
            'title': 'Hydrogen bonds',
            'body': 'If this option is checked, Mapiya calculates hydrogen bonds using EDHB.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'secondary_structure': {
            'title': 'Secondary structure',
            'body': 'If his option is checked, Mapiya calculates secondary structure using STRIDE.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'electrostatics': {
            'title': 'Electrostatics',
            'body': 'If this option is checked, Mapiya calculates electrostatics using Adaptive Poisson-Boltzmann Solve'
                    'r (APBS) software.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'add_atoms': {
            'title': 'Add atoms',
            'body': 'This option enables users to add missing atoms to the structure. The available options are: all, h'
                    'eavy, standard, terminal, hydrogen and none.',
            'icon': 'question-circle',
            'placement': 'left'
        },
        'add_residues': {
            'title': 'Add residues',
            'body': 'This option enables users to add missing residues to the structure. The available options are: all'
                    ', internal, terminal, none.',
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
            'body': 'This option enables users to keep heterogeneous atoms from being removed. The available options fo'
                    'r heterogens to be kept are: all, water, none.',
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
                    'amino acid code for an original residue - index of a residue that is being replaced - three-letter'
                    ' amino acid code for a mutated residue, protein chain id. For example VAL-7-ILE, A will mutate val'
                    'one 7 into isoleucine in chain A.',
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
                    'e to use.',
            'icon': 'question-circle',
            'placement': 'left'
        },
    }

    HELP_TEXT = {
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
        'hydrogen_bonds': True,
        'secondary_structure': True,
        'electrostatics': True,
        'bio_assembly': False
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
        label='&#8627; membrane position'
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

    bio_assembly = forms.BooleanField(
        required=False,
        label='Create separate projects for each biological assembly'
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

        pane1_col1 = layout.Div(
            layout.HTML('<h6 class="form-column-heading">Basic options</h6>'),
            layouts.RowField('contact_cutoff'),
            layouts.RowField('protonation_ph'),
            css_class='form-column-wrapper'
        )

        pane1_col2 = layout.Div(
            layout.HTML('<h6 class="form-column-heading">Advanced options</h6>'),
            layouts.BoolField('hydrogen_bonds'),
            layouts.BoolField('secondary_structure'),
            layouts.BoolField('electrostatics'),
            css_class='form-column-wrapper'
        )

        pane2_col1 = layout.Div(
            layout.HTML('<h6 class="form-column-heading">Fix structure</h6>'),
            layouts.RowField('add_atoms'),
            layouts.RowField('add_residues'),
            layouts.RowField('max_loop_length'),
            layouts.RowField('keep_heterogens'),
            layouts.RowField('replace_non_standard'),
            layouts.RowField('apply_mutations'),
            css_class='form-column-wrapper'
        )

        pane2_col2 = layout.Div(
            layout.HTML('<h6 class="form-column-heading">Add environment</h6>'),
            layouts.RowField('add_environment'),
            layouts.RowField('positive_ion'),
            layouts.RowField('negative_ion'),
            layouts.RowField('ionic_strength'),
            layouts.RowField('water_box'),
            layouts.RowField('box_dimensions'),
            layouts.RowField('lipid_type'),
            layouts.RowField('membrane_position'),
            css_class='form-column-wrapper'
        )

        submit_button = layouts.ButtonLink(
            href=reverse('reset-options'),
            text='Reset to defaults',
            css_class='btn btn-danger btn-sm'
        )

        tab1_header = '1. Select options'
        tab2_header = '2. Fix structure'
        tab3_header = '3. Biological assembly'

        nav_layout = layout.HTML(f'''
        <ul class="nav nav-tabs" id="myTab" role="tablist">
          <li class="nav-item" role="presentation">
            <a class="nav-link active" id="home-tab" data-toggle="tab" href="#pane1" role="tab">{tab1_header}</a>
          </li>
          <li class="nav-item" role="presentation">
            <a class="nav-link" id="profile-tab" data-toggle="tab" href="#pane2" role="tab">{tab2_header}</a>
          </li>
          <li class="nav-item" role="presentation">
            <a class="nav-link" id="profile-tab" data-toggle="tab" href="#pane3" role="tab">{tab3_header}</a>
          </li>
        </ul>
        ''')

        tabs_layout = layout.Div(
            layout.Div(
                layout.Div(
                    pane1_col1,
                    pane1_col2,
                    css_class='form-row-wrapper'
                ),
                css_class='tab-pane fade show active',
                css_id='pane1',
                role='tabpanel'
            ),
            layout.Div(
                layout.Div(
                    pane2_col1,
                    pane2_col2,
                    css_class='form-row-wrapper'
                ),
                css_class='tab-pane fade',
                css_id='pane2',
                role='tabpanel'
            ),
            layout.Div(
                layout.Div(
                    layouts.BoolField('bio_assembly'),
                    layout.HTML('''<small>
                        Clicking the option above will invoke the reconstruction of the biological assembl(y/ies) using
                        the information in the input file PDB ('REMARK 300 and 'REMARK 350').
                        More information is provided in the About section.
                    </small>'''),
                    css_class='form-row-wrapper'
                ),
                css_class='tab-pane fade',
                css_id='pane3',
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
