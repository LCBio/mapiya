from django.utils.html import format_html

TOOLTIPS = {
    'contact_cutoff': {
        'title': 'Contact cutoff',
        'body': '''
            Set the value for the contact cutoff (in angstrom [Å]). Two residues are considered in contact if the 
            distance between the two closest heavy atoms in two different residues is below the contact cutoff value.
            <br>In the project view, the user can later change this value and display contact maps for the changed 
            contact cutoff.
        ''',
    },
    'protonation_ph': {
        'title': 'Protonation pH',
        'body': '''
            Set the pH value for the modeled environment. The value can range between 0 and 14.
        ''',
    },
    'hydrogen_bonds': {
        'title': 'Hydrogen bonds',
        'body': '''
            Calculate hydrogen bonds using EDHB.
            <br><em>Verma N, Tao Y, Kraka E., J Phys Chem B. 2021;125(10):2551-2565</em><br>
            <strong>Note: The structure has to have hydrogens to calculate hydrogen bonds</strong>
        ''',
    },
    'secondary_structure': {
        'title': 'Secondary structure',
        'body': '''
            Calculate secondary structure using STRIDE.
        ''',
    },
    'electrostatics': {
        'title': 'Electrostatics',
        'body': '''
            Calculate electrostatics using Adaptive Poisson-Boltzmann Solver (APBS) software.
        ''',
    },
    'add_atoms': {
        'title': 'Add atoms',
        'body': '''
            Add missing atoms to the structure. Available options are:
            <ul>
                <li><strong>all</strong> - all missing atoms will be added to the structure</li>
                <li><strong>heavy</strong> - only non-hydrogen atoms will be added</li>
                <li><strong>standard</strong> - standard atoms will be added</li>
                <li><strong>terminal</strong> - only terminal atoms will be added</li>
                <li><strong>hydrogen</strong> - only hydrogen atoms will be added</li>
                <li><strong>none</strong> - no atoms will be added</li>
            </ul>   
        ''',
    },
    'add_residues': {
        'title': 'Add residues',
        'body': '''
            Add missing residues to the structure. Available options are:
            <ul>
                <li><strong>all</strong> - all missing residues will be added to the structure</li> 
                <li><strong>internal</strong> - missing residues will be added everywhere except for the terminal 
                    regions</li>
                <li><strong>terminal</strong> - only terminal missing residues will be added</li>
                <li><strong>none</strong> - no residues will be added</li>
            </ul>
        ''',
    },
    'max_loop_length': {
        'title': 'Max loop length',
        'body': '''
            Set the maximal length of inserted loops.
        ''',
    },
    'keep_heterogens': {
        'title': 'Keep heterogens',
        'body': '''
            This option enables users to keep heterogeneous atoms from being removed. The available options for 
            heterogens to be kept are: all, water, none.
        ''',
    },
    'replace_non_standard': {
        'title': 'Replace non-standard amino acids',
        'body': '''
            Replace all non-standard amino acids in the structure for their standard equivalents.
        ''',
    },
    'apply_mutations': {
        'title': 'Apply mutations',
        'body': '''
            This option enables users to apply mutations to the structure.<br>
            Input must be in the following format: <strong>XXX-NUM-YYY:ID</strong> where:
            <ul>
                <li><strong>XXX</strong> - three-letter amino acid code for the original residue</li>
                <li><strong>NUM</strong> - index of the residue that is being replaced</li>
                <li><strong>YYY</strong> - three-letter amino acid code for the mutated residue</li>
                <li><strong>ID</strong> - chain ID</li>
            </ul>
            For example: <strong>VAL-7-ILE:A</strong> will mutate Valine 7 in the chain A into Isoleucine.<br>
            Multiple mutations may be entered, separated by the comma.
        ''',
    },
    'add_environment': {
        'title': 'Add environment',
        'body': '''
            This option enables users to add an environment to a modeled project. The available options are: none, 
            solvent, membrane.
        ''',
    },
    'membrane_position': {
        'title': 'Membrane position',
        'body': '''
            This option enables users to specify the membrane position. The first number is the position along the Z 
            axis of the center of the membrane and the second number is the the minimal padding distance to use.
        ''',
    },
    'positive_ion': {
        'title': 'Positive ion',
        'body': '''
            Type of positive ion to put in the water box: 
            <ul>
                <li><strong>Cs+</strong></li>
                <li><strong>K+</strong></li>
                <li><strong>Li+</strong></li>
                <li><strong>Na+</strong></li>
                <li><strong>Rb+</strong></li>
            </ul>
        ''',
    },
    'negative_ion': {
        'title': 'Negative ion',
        'body': '''
            Type of negative ion to put in the water box: 
            <ul>
                <li><strong>Cl-</strong></li>
                <li><strong>Br-</strong></li>
                <li><strong>F-</strong></li>
                <li><strong>I-</strong></li>
            </ul>
        ''',
    },
    'ionic_strength': {
        'title': 'Ionic strength',
        'body': '''
            The molar concentration of ions (both positive and negative) to put in the water box.
            Ions that are added to neutralize the system are not included. 
        ''',
    },
    'lipid_type': {
        'title': 'Lipid type',
        'body': '''
            Type of lipid to add: 
            <ul>
                <li><strong>POPC</strong></li>
                <li><strong>POPE</strong></li>
                <li><strong>DLPC</strong></li>
                <li><strong>DLPE</strong></li>
                <li><strong>DMPC</strong></li>
                <li><strong>DOPC</strong></li>
                <li><strong>DPPC</strong></li>
            </ul>
        ''',
    },
    'water_box': {
        'title': 'Water box',
        'body': '''
            The type of the box to fill with water:
            <ul>
                <li><strong>Unit cell</strong></li>
                <li><strong>Max size</strong></li>
                <li><strong>Custom</strong> (must specify box dimensions)</li>
            </ul>
            
        ''',
    },
    'box_dimensions': {
        'title': 'Box dimensions',
        'body': '''
            The box dimensions in nm <strong>[X Y Z]</strong>.
        ''',
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
