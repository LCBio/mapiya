from django.utils.html import format_html

TOOLTIPS = {
    'contact_cutoff': {
        'title': 'Contact cutoff',
        'body': '''
            User sets the value for contact cutoff (in angstrom [Å]). The distance between the two closest heavy atoms 
            in two different residues is considered contact if it is below the contact cutoff value. In the project 
            view for a particular file, the user can later change this value and display contact maps for the changed 
            contact cutoff.
        ''',
    },
    'protonation_ph': {
        'title': 'Protonation pH',
        'body': 'The user sets the value for pH of the modeled environment. The value can range between 0 and 14.',
    },
    'hydrogen_bonds': {
        'title': 'Hydrogen bonds',
        'body': 'If this option is checked, Mapiya calculates hydrogen bonds using EDHB.',
    },
    'secondary_structure': {
        'title': 'Secondary structure',
        'body': 'If his option is checked, Mapiya calculates secondary structure using STRIDE.',
    },
    'electrostatics': {
        'title': 'Electrostatics',
        'body': 'If this option is checked, Mapiya calculates electrostatics using Adaptive Poisson-Boltzmann Solve'
                'r (APBS) software.',
    },
    'add_atoms': {
        'title': 'Add atoms',
        'body': 'This option enables users to add missing atoms to the structure. The available options are: all, h'
                'eavy, standard, terminal, hydrogen and none.',
    },
    'add_residues': {
        'title': 'Add residues',
        'body': 'This option enables users to add missing residues to the structure. The available options are: all'
                ', internal, terminal, none.',
    },
    'max_loop_length': {
        'title': 'Max loop length',
        'body': 'This option enables users to specify the maximal length of inserted loops.',
    },
    'keep_heterogens': {
        'title': 'Keep heterogens',
        'body': 'This option enables users to keep heterogeneous atoms from being removed. The available options fo'
                'r heterogens to be kept are: all, water, none.',
    },
    'replace_non_standard': {
        'title': 'Replace non-standard amino acids',
        'body': 'This option enables users to replace all non-standard amino acids in the structure for their stand'
                'ard equivalents.',
    },
    'apply_mutations': {
        'title': 'Apply mutations',
        'body': 'This option enables users to apply mutations in the structure. The input is in form: three-letter '
                'amino acid code for an original residue - index of a residue that is being replaced - three-letter'
                ' amino acid code for a mutated residue, protein chain id. For example VAL-7-ILE, A will mutate val'
                'one 7 into isoleucine in chain A.',
    },
    'add_environment': {
        'title': 'Add environment',
        'body': 'This option enables users to add an environment to a modeled project. The available options are: n'
                'one, solvent, membrane.',
    },
    'membrane_position': {
        'title': 'Membrane position',
        'body': 'This option enables users to specify the membrane position. The first number is the position along'
                ' the Z axis of the center of the membrane and the second number is the the minimal padding distanc'
                'e to use.',
    },
}


def format_tooltip(name):
    if tooltip := TOOLTIPS.get(name):
        placement = tooltip.get('placement', 'right')
        title = tooltip.get('title', 'Title')
        body = tooltip.get('body', 'Example tooltip')

        content = format_html(f'''
            <h6 class='tooltip-title'>{title}</h6>    
            <div class='tooltip-body'>{body}</div>
        ''')

        return f'data-toggle="tooltip" data-html="true" data-placement="{placement}" title="{content}"'
    return ''
