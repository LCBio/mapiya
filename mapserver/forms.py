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


class OptionsForm(forms.Form):

    contact_cutoff = forms.FloatField(
        min_value=0,
        max_value=20.0,
        widget=forms.NumberInput(attrs={'step': 0.1}),
        initial=8.0,
        label='contact cutoff [&#8491;]'
    )

    add_atoms = forms.ChoiceField(
        choices=[
            (0, 'all'),
            (1, 'heavy'),
            (2, 'standard'),
            (3, 'terminal'),
            (4, 'hydrogen'),
            (5, 'none')
        ],
        initial=5,
        label='add atoms'
    )

    protonation_ph = forms.FloatField(
        min_value=0,
        max_value=14.0,
        widget=forms.NumberInput(attrs={'step': 0.1}),
        initial=7.0,
        label='&#8627; protonation pH'
    )

    add_residues = forms.ChoiceField(
        choices=[
            (0, 'all'),
            (1, 'internal'),
            (2, 'terminal'),
            (3, 'none'),
        ],
        initial=3,
        label='add residues'
    )

    max_loop_length = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=5,
        label='&#8627; max loop length'
    )

    keep_heterogens = forms.ChoiceField(
        choices=[
            (0, 'all'),
            (1, 'water'),
            (2, 'none')
        ],
        initial=2,
        label='keep heterogens'
    )

    replace_non_standard = forms.BooleanField(
        widget=forms.Select(choices=((True, 'yes'), (False, 'no'))),
        initial=False,
        label='replace non-standard aa'
    )

    apply_mutations = forms.BooleanField(
        widget=forms.Select(choices=((True, 'yes'), (False, 'no'))),
        initial=False,
        label='apply mutations'
    )

    specify_mutations = forms.CharField(
        label='&#8627; specify mutations',
        widget=forms.TextInput(attrs={'placeholder': 'e.g., VAL-3-ILE:A, ILE-7-VAL:A'})
    )

    add_environment = forms.ChoiceField(
        choices=[
            (0, 'solvent'),
            (1, 'membrane'),
            (2, 'none')
        ],
        initial=2,
        label='add environment'
    )

    positive_ion = forms.ChoiceField(
        choices=[
            (0, 'Na+'),
            (1, 'Cs+'),
            (2, 'K+'),
            (3, 'Li+'),
            (4, 'Rb+'),
        ],
        initial=0,
        label='&#8627; positive ion'
    )

    negative_ion = forms.ChoiceField(
        choices=[
            (0, 'Cl-'),
            (1, 'Br-'),
            (2, 'F-'),
            (3, 'I-'),
        ],
        initial=0,
        label='&#8627; negative ion'
    )

    water_box = forms.ChoiceField(
        choices=[
            (0, 'unit cell'),
            (1, 'max size'),
            (2, 'custom'),
        ],
        initial=0,
        label='&#8627; water box'
    )

    box_dimensions = forms.CharField(
        # TODO: change to triple input field WxHxD
        widget=forms.TextInput(
            attrs={'placeholder': '5,5,5'}
        ),
        label='&#8627; box dimensions'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = helper.FormHelper()
        self.helper.attrs = {'novalidate': ''}
        self.helper.form_show_errors = True
        self.helper.form_show_labels = True
        self.helper.use_custom_control = True
        self.helper.form_tag = False
        self.helper.label_class = 'col-4 small'
        self.helper.field_class = 'col-8'

        self.helper.layout = layout.Column(
            layout.HTML('<h6 class="ml-3">Options:</h6>'),
            layouts.RowField('contact_cutoff'),
            layouts.HR,
            layout.HTML('<h6 class="ml-3">Fix PDB file with PDBfixer:</h6>'),
            layouts.RowField('add_atoms'),
            layouts.RowField('protonation_ph'),
            layouts.RowField('add_residues'),
            layouts.RowField('max_loop_length'),
            layouts.RowField('keep_heterogens'),
            layouts.RowField('replace_non_standard'),
            layouts.RowField('apply_mutations'),
            layouts.RowField('specify_mutations'),
            layouts.RowField('add_environment'),
            layouts.RowField('positive_ion'),
            layouts.RowField('negative_ion'),
            layouts.RowField('box_dimensions'),
            layouts.RowField('water_box'),
            layouts.HR,
            layout.Reset('reset', 'Reset to defaults', css_class='btn btn-danger btn-block')
        )
