import json

from django import forms
from django.urls import reverse
from crispy_forms import layout, helper
from . import layouts


class OptionsForm(forms.Form):

    DEFAULTS = {
        'contact_cutoff': 8.0,
        'protonation_ph': 7.0,
        'add_atoms': 'all',
        'add_residues': 'internal',
        'max_loop_length': 5,
        'keep_heterogens': 'none',
        'replace_non_standard': True,
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
        widget=forms.TextInput(attrs={'placeholder': 'e.g., VAL-3-ILE:A'})
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

    hydrogen_bonds = forms.ChoiceField(
        choices=[(False, 'no'), (True, 'yes')],
        label='Hydrogen bonds'
    )

    secondary_structure = forms.ChoiceField(
        choices=[(False, 'no'), (True, 'yes')],
        label='Secondary structure'
    )

    electrostatics = forms.ChoiceField(
        choices=[(False, 'no'), (True, 'yes')],
        label='Electrostatics'
    )

    bio_assembly = forms.BooleanField(
        required=False,
        label='Create separate projects for each biological assembly'
    )

    def clean_replace_non_standard(self):
        return self.cleaned_data['replace_non_standard'] in ['True', 'true', True]

    def clean_hydrogen_bonds(self):
        return self.cleaned_data['hydrogen_bonds'] in ['True', 'true', True]

    def clean_secondary_structure(self):
        return self.cleaned_data['secondary_structure'] in ['True', 'true', True]

    def clean_electrostatics(self):
        return self.cleaned_data['electrostatics'] in ['True', 'true', True]

    def clean_apply_mutations(self):
        return self.cleaned_data['apply_mutations'].upper()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            layouts.RowField('hydrogen_bonds'),
            layouts.RowField('secondary_structure'),
            layouts.RowField('electrostatics'),
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
                layout.Field(
                    'bio_assembly',
                    template='bioassembly.html',
                    css_class='custom-control-input'
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
