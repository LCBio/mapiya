#import sys ###
import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import json
import os
from pathlib import Path
import plotly.graph_objects as go
from dash.dash import no_update
from dash.dependencies import Input, State, Output
from dash.exceptions import PreventUpdate
from datetime import datetime  # to be removed
from django_plotly_dash import DjangoDash

from mollib.chord import *
from mollib.patterns import * #calc_patterns, calc_entropy
#from .models import Job
from . import views

#np.set_printoptions(threshold=sys.maxsize)				### testing mode
#    print('Start... ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))	### testing mode

# CSS style
drops = {'margin': '0 0 0.4vh 2vw', 'width': '13vw', 'display': 'inline-block', 'font-size': '2vh',
         'font-family': 'Ubuntu, sans-serif', 'color': 'dimgrey'}
lab_style = {'color': '#63533c', 'text-align': 'left', 'font-size': '0.85rem', 'font-weight': '500',
             'margin-left': '2px', 'font-family': 'Ubuntu, sans-serif'}
btn_basic = {'margin': '0 0.5vw 0 0', 'padding': '0.2vh 0', 'font-size': '2vh', 'height': '3vh', 'width': '7vw'}
btn_style = {'background-color': '#eeece7', 'color': '#63533c'}
btn_selected_style = {'borderBottom': '3px solid #4682B4', 'borderTop': '0px solid #4682B4',
                      'background-color': '#95C8D8', 'color': 'black'}
btn_disabled_style = {'background-color': '#F8F9F9', 'color': '#95A5A6'}
btn_opts = {'height': '4vw', 'width': '4vw', 'border': '1px', 'margin-bottom': '0.45vw', 'font-size': '3vh'}
btn_slider = {'height': '3vh', 'width': '4vw', 'display': 'inline-block', 'position': 'absolute', 'top': '0',
              'font-size': '1.7vh'}
tabs_style = {'height': '4vh', 'width': '89.5vw', 'overflow-x': 'hidden', 'overflow-y': 'hidden',
              'scrollbar-width': 'none', 'display': 'inline-block', 'margin-left': '4.5vw', 'margin-right': '0.5vw'}
settings_style = {'width': 'fit-content', 'height': 'auto', 'display': 'block', 'background': '#eeece7', 'opacity': '0.95',
                  'border-radius': '5px 5px 5px 5px', 'position': 'absolute', 'top': '0', 'left': '0.5vw', 'z-index': '101',
                  'padding': '1vh 1vw 1vh 1vw'}
settings_close = {'margin': '0 1vw 0 0', 'border': '0px', 'color': '#63533c', 'font-size': '3vh', 'vertical-align': 'top', 
                  'height':'2vw', 'width':'2vw', 'position':'absolute', 'top':'0', 'right':'0', 'z-index':'105'}

# colorscales
colors = ['ice', 'Viridis', 'Cividis', 'Inferno', 'Magma', 'Plasma', 'Turbo', 'Blackbody', 'Blured', 'Electric', 'Hot', 'Jet',
          'Rainbow', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PuBu', 'PuBuGn', 'PuRd',
          'Purples', 'RdBu', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'turbid', 'thermal', 'haline',
          'solar', 'gray', 'deep', 'dense', 'algae', 'matter', 'speed', 'amp', 'tempo', 'Burg', 'Burgyl',
          'Redor', 'Oryel', 'Peach', 'Pinkyl', 'Mint', 'Blugrn', 'Darkmint', 'Emrld', 'Aggrnyl', 'Bluyl', 'Teal',
          'Tealgrn', 'Purp', 'Purpor', 'Sunset', 'Magenta', 'Sunsetdark', 'Agsunset', 'Brwnyl']
colors_binary = {'Purple': 'rgb(128,0,128)', 'Fuchsia': 'rgb(255,0,255)', 'Navy': 'rgb(0,0,128)', 'Blue': 'rgb(0,0,255)', 'Skyblue': 'rgb(29,172,214)', 
          'Teal': 'rgb(0,128,128)', 'Aqua': 'rgb(0,255,255)', 'Green': 'rgb(0,128,0)', 'Lime': 'rgb(0,255,0)', 'Olive': 'rgb(128,128,0)', 'Yellow': 'rgb(255,255,0)',
          'Orange': 'rgb(255,128,0)', 'Maroon': 'rgb(128,0,0)', 'Red': 'rgb(255,0,0)', 'Silver': 'rgb(192,192,192)', 'Gray': 'rgb(128,128,128)', 'Black': 'rgb(0,0,0)'}
cs_seq = [[0, "rgb(210,255,0)"], [0.05, "rgb(210,255,0)"], [0.051, "rgb(255,255,0)"], [0.1, "rgb(255,255,0)"],
          [0.101, "rgb(250,220,10)"], [0.15, "rgb(250,220,10)"], [0.151, "rgb(255,160,25)"], [0.2, "rgb(255,160,25)"],
          [0.201, "rgb(240,110,0)"], [0.25, "rgb(240,110,0)"], [0.251, "rgb(225,0,0)"], [0.3, "rgb(225,0,0)"],
          [0.301, "rgb(175,5,0)"], [0.35, "rgb(175,5,0)"], [0.351, "rgb(220,0,75)"], [0.4, "rgb(220,0,75)"],
          [0.401, "rgb(255,35,150)"], [0.45, "rgb(255,35,150)"], [0.451, "rgb(255,0,255)"], [0.5, "rgb(255,0,255)"],
          [0.501, "rgb(190,0,215)"], [0.55, "rgb(190,0,215)"], [0.551, "rgb(115,0,160)"], [0.6, "rgb(115,0,160)"],
          [0.601, "rgb(15,15,130)"], [0.65, "rgb(15,15,130)"], [0.651, "rgb(30,30,220)"], [0.7, "rgb(30,30,220)"],
          [0.701, "rgb(0,130,255)"], [0.75, "rgb(0,130,255)"], [0.751, "rgb(0,195,255)"], [0.8, "rgb(0,195,255)"],
          [0.801, "rgb(100,255,255)"], [0.85, "rgb(100,255,255)"], [0.851, "rgb(0,240,170)"], [0.9, "rgb(0,240,170)"],
          [0.901, "rgb(0,190,0)"], [0.95, "rgb(0,190,0)"], [0.951, "rgb(80,130,0)"], [0.999, "rgb(80,130,0)"], [1, "rgb(0,0,0)"]]
cs_ss8 = [[0, "rgb(30,140,35)"], [0.13, "rgb(30,140,35)"], [0.131, "rgb(100,185,40)"], [0.25, "rgb(100,185,40)"],
          [0.251, "rgb(200,255,50)"], [0.37, "rgb(200,255,50)"], [0.371, "rgb(215,0,65)"], [0.50, "rgb(215,0,65)"],
          [0.501, "rgb(255,50,150)"], [0.63, "rgb(255,50,150)"], [0.631, "rgb(255,100,255)"], [0.75, "rgb(255,100,255)"],
          [0.751, "rgb(160,140,255)"], [0.87, "rgb(160,140,255)"], [0.871, "rgb(90,220,255)"], [0.999, "rgb(90,220,255)"], [1, "rgb(0,0,0)"]]
cs_sa = [[0, "rgb(215,0,0)"], [0.2, "rgb(215,0,0)"], [0.25, "rgb(155,155,255)"], [0.4, "rgb(155,155,255)"],
         [0.5, "rgb(155,155,255)"], [0.8, "rgb(0,0,105)"], [0.99, "rgb(0,0,105)"], [1, 'rgb(0,0,0)']]
cs_polar = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(255,85,85)'], [1, 'rgb(255,85,85)']]
cs_npolar = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(50,165,220)'], [1, 'rgb(50,165,220)']]
cs_pi = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(255,100,0)'], [1, 'rgb(255,100,0)']]
cs_aromatic = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(255,205,0)'], [1, 'rgb(255,205,0)']]
cs_hdonor = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(50,165,220)'], [1, 'rgb(50,165,220)']]
cs_haccep = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(255,50,155)'], [1, 'rgb(255,50,155)']]
cs_phobic = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(50,165,220)'], [1, 'rgb(50,165,220)']]
cs_amphi = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(180,0,180)'], [1, 'rgb(180,0,180)']]
cs_philic = [[0, 'rgb(255,255,255)'], [0.5, 'rgb(255,255,255)'], [0.501, 'rgb(255,85,85)'], [1, 'rgb(255,85,85)']]
cs_charge = [[0, 'rgb(255,255,255)'], [0.33, 'rgb(255,255,255)'], [0.331, 'rgb(215,0,0)'], [0.66, 'rgb(215,0,0)'], [0.661, 'rgb(0,0,105)'], [1, 'rgb(0,0,105)']]
cs_sulfur = [[0, 'rgb(255,255,255)'], [0.33, 'rgb(255,255,255)'], [0.331, 'rgb(0,190,0)'], [0.66, 'rgb(0,190,0)'], [0.661, 'rgb(0,240,170)'], [1, 'rgb(0,240,170)']]
cs_rdbu = [[0, "rgb(103,0,31)"], [0.1, "rgb(178,24,43)"], [0.2, "rgb(214,36,77)"], [0.3, "rgb(244,165,130)"],
           [0.4, "rgb(253,219,199)"], [0.5, "rgb(247,247,247)"], [0.6, "rgb(209,229,240)"],
           [0.7, "rgb(146,197,222)"], [0.8, "rgb(67,147,195)"], [0.9, "rgb(33,102,172)"], [1, "rgb(5,48,97)"]]
cs_gnbu = [[0, "rgb(247,252,240)"], [0.125, "rgb(224,243,219)"], [0.25, "rgb(204,235,197)"],
           [0.375, "rgb(168,221,181)"], [0.5, "rgb(123,204,196)"], [0.625, "rgb(78,179,211)"],
           [0.75, "rgb(43,140,190)"], [0.875, "rgb(8,104,172)"], [1, "rgb(8,64,129,1)"]]



# const. data
amino = ['W', 'F', 'Y', 'N', 'Q', 'D', 'E', 'S', 'T', 'H', 'K', 'R', 'L', 'I', 'V', 'A', 'G', 'M', 'C', 'P']

title = {'basic_opts' : 'Set basic parameters of the chart, such as:\n• display mode,\n• contact cutoff,\n• color scale.',
         'intra-map' : 'The intramolecular map shows the internal contacts of the object.\n\
These contacts stabilize the secondary structure and topology of a single domain.',
         'inter-map' : 'The intermolecular map shows the spatial contacts between two different objects.\n\
These contacts define binding interfaces, stabilize the quaternary structure,\nand are important for function.',
         'display-mode' : 'Select mode to display:\n• CM - Contact Map (intra- or intermolecular), where only \
points below the cutoff are visible\n• DM - Distance Map (intra- or intermolecular), where all points are \
colored by distance\n• CM | DM - Mixed Map (intramolecular only), split between top-left Contact Map triangle\n\
    and bottom-right Distance Map triangle',
         'cutoff' : 'Select distance cutoff [Å] below which contacts will be defined.\ndefault: 8.0 Å',
         'color-scale' : 'Select a continuous color scale for the Distance Map\n\
or a discrete color for the Contact Map visualization.',
         'reverse-cs' : 'Reverse the color order in the selected color scale.',
         'smoth-cs' : 'Convert the selected color to a continuous color scale fading to white.\n\
This will visually distinguish between contacts closer and more distant in space.',
         'filters' : 'Select filters that reduce the number of displayed contacts.',
         'intra-filter' : 'Filter out local contacts between neighboring residues.\n\
As a result, the points along diagonal are dropped.\nThe filter takes an integer n, which defines the number \
of amino acids (i, i+1, ..., i+n)\nalong the sequence, for which contacts are excluded.\n\
The filter is available only for intramolecular maps (internal contacts for an object).\ndefault: n = 0',
         'interaction-filter' : 'Highlight the protein-protein contacts stabilized by the selected interaction type.\n\
This facilitates your discovery of the nature of the interaction.\nEach option in the Interaction Filter has its own tooltip.\
\n\nNote: Some contacts can be multivalent (e.g., have both charge and π-electrons)\nand can be displayed for several \
force types (e.g., electrostatics and π-stacking).\nMost filters are defined on-the-fly based on the physicochemical properties\n\
of amino acid side groups. Hydrogen bonds are calculated using EDHB.\nFilters for interactions with other \
biomacromolecules will be available\nin the next version of the Mapiya, so check out it frequently.\n',
         'interaction-only' : 'Display filtered contacts only.\nThis removes the other contacts from the background of the plot.',
         'features' : 'Select one-dimensional features to be displayed along the sequence.',
         'feature-y' : 'Select the additional feature assigned with the residue-resolution along the protein sequence.\n\
The bar-chart will be displayed on the right side parallel to the Y axis.\n\nAvailable options include:\n\
• various physicochemical properties,\n• amino acid composition,\n• secondary structure, calculated using STRIDE,\n\
• solvent accessibility, calculated using STRIDE,\n• Shannon enthropy, calculated on-the-fly,\n\
• hydrogen bond donor/acceptor,\n• and more.',
         'feature-x' : 'Select the additional feature assigned with the residue-resolution along the protein sequence.\n\
The bar-chart will be displayed on the top side parallel to the X axis.\n\nAvailable options include:\n\
• various physicochemical properties,\n• amino acid composition,\n• secondary structure, calculated using STRIDE,\n\
• solvent accessibility, calculated using STRIDE,\n• Shannon enthropy, calculated on-the-fly,\n\
• hydrogen bond donor/acceptor,\n• and more.',
         'hydropathy' : 'The hydropathy shows the hydrophobic (lacking affinity for water),\n\
amphipatic (having both polar-water-soluble and nonpolar-not-water-soluble regions),\n\
and hydrophilic (attracted to water) tendencies of the protein sequence.\n\
The hydrophobic (Φ) amino acids are: Gly, Ala, Leu, Ile, Val, Pro, Phe.\n\
The amphipatic (ɤ) amino acids are: Trp, Tyr, Met, Lys.\n\
The hydrophilic (ζ) amino acids are: Arg, Asn, Asp, Gln, Glu, His, Ser, Thr, Cys.',
         'hydrophobic' : 'Hydrophobicity is the physical property of a molecule that is seemingly repelled from water.\n\
The hydrophobic (Φ) amino acids are: Gly, Ala, Leu, Ile, Val, Pro, Phe.\n',
         'hydrophilic' : 'Hydrophilic substances have a strong affinity for water and dissolve in water.\n\
The hydrophilic (ζ) amino acids are: Arg, Asn, Asp, Gln, Glu, His, Ser, Thr, Cys.',
         'electrostatics' : 'Electrostatics describes the interactions between charges.\n\
There is an attractive (A) force between a positive ⊕ and a negative ⊖ charge,\nwhile two charges of the same sign repel (R) each other. \
Point charges (monopoles)\nsuch as ions ⦿ , can also interact electrostatically with dipoles (e.g., polar groups, δ)\n\
and cause temporary charge shifts (induced dipoles) in neutral groups.\nPositively charged amino acids, ⊕ are: Arg, Lys, His.\n\
Negatively charged amino acids, ⊖ are: Glu, Asp.\nPolar amino acids, δ are: Ser, Thr, Tyr, Gln, Asn, Cys, Met.',
         'pi-stacking' : 'π–π stacking is an attractive, noncovalent interaction between\naromatic rings, ⌬ , \
and/or other π–electron-containing systems.\nThe aromatic amino acids, ⌬ are: Phe, Tyr, trp, His.\n\
The other systems with π–bond are: Arg, Asn, Asp, Gln, Glu, Gly*.',
         'ion-stacking' : 'Ion–π interaction is a noncovalent attractive interaction between the electron-rich π-system\n\
(e.g. aromatic ring ⌬ or other π-bond) and an adjacent ion, i.e., cation ⊕ or anion ⊖.\n\
The aromatic amino acids, ⌬ are: Phe, Tyr, trp, His.\nThe other systems with π–bond are, π: Arg, Asn, Asp, Gln, Glu, Gly*.\n\
The charged amino acids are: ⊕ : Arg, Lys, His, and ⊖ : Glu, Asp.\n\n\
The ion-π interactions are orientation-dependent. The two most stable conformations\nare the parallel displaced and T-shaped.\n\
The stacking is also possible between π–electron-containing system and polar group\nor even C-H orbital.',
         'hbonds' : 'A hydrogen bond is a special type of dipole-dipole attraction, involving a hydrogen atom\n\
located between a pair of highly electronegative atoms (having a high affinity for electrons).\n\
Hydrogen bonds are calculated using EDHB. If the option is disabled, the process was unsuccessful.\n\
Amino acids that can be proton donors: Arg, Asn, Gln, His, Ser, Thr, Tyr, Trp, Cys, Lys.\n\
Amino acids that can be proton acceptors: Asn, Asp, Gln, Glu, His, Ser, Thr, Tyr.',
         'title': 'Enter a customized title that will display above the chart.',
}

params = {'composition': [cs_seq, 'SEQUENCE', 0.45, [0.02, 0.07, 0.12, 0.17, 0.22, 0.27, 0.32, 0.37, 0.42, 0.47,
                                            0.52, 0.57, 0.62, 0.67, 0.72, 0.77, 0.82, 0.87, 0.92, 0.97], amino],
          'hydropathy': [cs_rdbu, 'HYDROPATHY', 0.15, [0.1, 0.5, 0.9], ['-4.5 (philic)', '0.0', '4.5 (phobic)']],
          'hydropathy_n': [cs_rdbu, 'HYDROPATHY-n', 0.15, [0.1, 0.5, 0.9], ['0 (philic)', '0.5', '1 (phobic)']],
          'hydrophobic': [cs_phobic, 'HYDROPHOBIC', 0.12, [0.25, 0.75], ['NO', 'YES']],
          'amphipatic': [cs_amphi, 'AMPHIPATIC', 0.12, [0.25, 0.75], ['NO', 'YES']],
          'hydrophilic': [cs_philic, 'HYDROPHILIC', 0.12, [0.25, 0.75], ['NO', 'YES']],
          'charged': [cs_charge, 'CHARGE', 0.15, [0.17, 0.5, 0.83], ['NO', 'positive', 'negative']],
          'polar': [cs_polar, 'POLAR', 0.12, [0.25, 0.75], ['NO', 'YES']],
          'nonpolar': [cs_npolar, 'NONPOLAR', 0.12, [0.25, 0.75], ['NO', 'YES']],
          'aromatic': [cs_aromatic, 'AROMATIC', 0.12, [0.25, 0.75], ['NO', 'YES']],
          'π-bond': [cs_pi, 'non-aromatic<br>π-BOND', 0.15, [0.25, 0.75], ['NO', 'YES']],
          'sulfur': [cs_sulfur, 'SULFUR', 0.15, [0.17, 0.5, 0.83], ['NO', 'CYS', 'MET']],
          'H-Bond donor': [cs_hdonor, 'H-BOND DONOR', 0.12, [0.25, 0.75], ['NO', 'YES']],
          'H-Bond acceptor': [cs_haccep, 'H-BOND ACCEPTOR', 0.12, [0.25, 0.75], ['NO', 'YES']],
          'SEQ entropy': [cs_gnbu, 'ENTROPY', 0.15, [], []],
          'II-structure': [cs_ss8, 'II-STRUCTURE', 0.25, [0.06, 0.19, 0.31, 0.43, 0.56, 0.69, 0.81, 0.93], 
                          ["ɑ-helix", "310-helix", "π-helix", "β-strand", "β-bridge", "HB-turn", "bend", 'loop']],
          'solvent access': [cs_sa, 'RSA', 0.15, [0.1, 0.35, 0.7], ['buried', 'medium', 'exposed']]
          }
opt_1D = ['none', 'composition', 'hydropathy', 'hydropathy_n', 'hydrophobic', 'amphipatic', 'hydrophilic', 'charged',
          'polar', 'nonpolar', 'aromatic', 'π-bond', 'sulfur', 'H-Bond donor', 'H-Bond acceptor',
          'SEQ entropy', 'II-structure', 'solvent access']


def get_objects_in_contact(selected):
    
    selected = selected.split('|')
    obj_a = selected[0].split(':')[0]
    obj_b = obj_a
    if len(selected) > 1:
        obj_b = selected[1].split(':')[0]
    return obj_a, obj_b

##########################################################


app = DjangoDash('ContactMap')
app.css.append_css({'external_url': '/static/css/app.css'})

app.layout = html.Div([
    dcc.Input(id="input-pk", value='', type='hidden'),  # current pk - initial input from django
    dcc.Input(id="interval_status", value=1, type='hidden'),  # fire callback until all models have 'F' status
    dcc.Input(id="model-ix", value='', type='hidden'),  # index of selected model
    dcc.Input(id="selected", value='', type='hidden'),  # selected object or interaction
    dcc.Store(id="pdb-code", data='', storage_type='session'), # PDB code or filename
    dcc.Store(id="config", data='', storage_type='session'), # main settings for external software
    dcc.Store(id="model-data", data='', storage_type='session'),  # [info, matrix_path, struct_path, hbond_path]
    dcc.Store(id="con-intra", data='', storage_type='session'),  # intramolecular contacts (options1)
    dcc.Store(id="con-inter", data='', storage_type='session'),  # intermolecular contacts (options2)
    dcc.Store(id="contacts", data='', storage_type='session'),  # list of objects + matrix of contacts counts
    dcc.Store(id="data_1d", data='', storage_type='session'),  # dict of features for 1D plots
    dcc.Store(id="data_Dist", data='', storage_type='session'),  # list = [desc_d, residuesA, residuesB, objA, objB]
    dcc.Store(id="data_Con", data='', storage_type='session'),  # contacts for selected cutoff
    dcc.Store(id="colors_1d", data='', storage_type='session'), # residues colors according to selected param-1d
    dcc.Store(id="colors_con", data='', storage_type='session'), # residues colors according to selected contact filter
    dcc.Input(id="hbonds", value='', type='hidden'),  # path to hbonds
    dcc.Input(id="download-text", value='', type='hidden'),  # list = [distances, desc_c, cutoff]
    dcc.Input(id="void1", value='', type='hidden'),
    dcc.Input(id="void2", value='', type='hidden'),
    dcc.Input(id="void3", value='', type='hidden'),
    dcc.Input(id="void4", value='', type='hidden'),
    dcc.Input(id="void5", value='', type='hidden'),
    dcc.Input(id="void6", value='', type='hidden'),
    dcc.Input(id="slider", value='', type='hidden'),

    dcc.Interval(id="interval", interval=5000),
    html.Div([
        html.Button('⯇', id="slideBack", type="button", style={'display': 'none'}),
        html.Div([html.Div(id='protein-models')], id='proteins'),
        html.Button('⯈', id="slide", type="button", style={'display': 'none'}),
    ], style={'position': 'relative'}),
    html.Div([
        html.Button('⚙', id='opts', className='hovertext', style={**btn_basic, **btn_style, **btn_opts}, title='display settings'),
        html.Button('✾', id='tab-1', style={**btn_basic, **btn_style, **btn_opts},
                    title='see objects and interactions'),
        html.Button('◩', id='tab-2', style={**btn_basic, **btn_style, **btn_opts, 'color': '#95A5A6'},
                    title='see contact map'),
        html.Button('⟱', id='tab-3', style={**btn_basic, **btn_style, **btn_opts}, title='download data'),
        html.Div([html.Div(id='settings', style={'display':'block', 'z-index':'110'}),
                  html.Button('×', id='close', style={**btn_style, **settings_close}, title='close options window'),
                 ], id='settings-dir', style={**settings_style, 'left': '4.5vw', 'min-width': '45vw'}),
    ], style={'width': '4vw', 'position': 'absolute', 'left': '0', 'z-index': '100'}),
    html.Div(id='tabs', style={'height': '93vh'}),
], style={'height': '97vh', 'width': '96vw', 'margin': '0', 'padding': '0'})


app.clientside_callback(
    """
    function (n_intervals) {
      document.getElementsByTagName("body")[0].style = 'margin: 0 !important';
    };
    """,
    Output('void1', 'value'), [Input("interval", "n_intervals")]
)


@app.expanded_callback(Output('slider', 'value'), [Input('slide', 'n_clicks'), Input('slideBack', 'n_clicks')])
def slide_models(left, right):
    if left is not None or right is not None:
        ctx = dash.callback_context
        button = ctx.triggered[0]['prop_id'].split('.')[0]
        if button == 'slide':
            return 'left'
        elif button == 'slideBack':
            return 'right'
    else:
        raise PreventUpdate


app.clientside_callback(
    """
    function (value) {
      if (value != '') {
        var element = document.getElementById('proteins');
        scrollAmount = 0;
        var slideTimer = setInterval(function(){
            if (value == 'left') {
                element.scrollLeft += 10;
            }
            else {
                element.scrollLeft -= 10;
            }
            scrollAmount += 10;
            if (scrollAmount >= 100) {
                window.clearInterval(slideTimer);
            }
        }, 25);
      }
    };
    """,
    Output('void2', 'value'), [Input('slider', 'value')]
)


app.clientside_callback(
    """
    function (n_clicks, n_clicks) {
      var targetDiv = document.getElementById("settings-dir");
      if (targetDiv.style.display !== "none" && typeof (n_clicks) !== 'undefined') {
          targetDiv.style.display = "none";
        } else {
          targetDiv.style.display = "block";
        }
    };
    """,
    Output('void3', 'value'), [Input('opts', 'n_clicks'), Input('close', 'n_clicks')]
)


app.clientside_callback(
    """
    function (value) {
      window.sessionStorage.setItem("model-ix", value);
    };
    """,
    Output('void4', 'value'), [Input('model-ix', 'value')]
)


app.clientside_callback(
    """
    function (value) {
      window.sessionStorage.setItem("chains-colors", value);
    };
    """,
    Output('void5', 'value'), [Input('chains-colors', 'value')]
)


app.clientside_callback(
    """
    function (value) {
      window.sessionStorage.setItem("click-map", value);
    };
    """,
    Output('void6', 'value'), [Input('click-map', 'value')]
)


@app.expanded_callback(
    [Output('interval_status', 'value'), Output('pdb-code', 'data'), Output('config', 'data'),
     Output('protein-models', 'children'), Output('proteins', 'style'), Output('slide', 'style'), Output('slideBack', 'style')],
    [Input('input-pk', 'value'), Input("interval", "n_intervals")], 
     State('model-ix', 'value'))
def load_models(pk, n, model_ix, **kwargs):

    project_data = json.loads(views.project_data(kwargs['request'],pk).getvalue().decode())	#dict of keys: 'filename', 'config', 'jobs': 'index' & 'status'
    project_data['pk'] = pk
    models = {}
    status = 0
    for i in project_data['jobs']:
        models[i['index']] = i['status']
    n_models = len(models)
    if n_models > 1:
        buttons = []
        if n_models <= 20:
            for i in models:
                if models[i] == 'F':
                    if model_ix == '':
                        model_ix = i
                    buttons.append(
                        dcc.Tab(label='M' + str(i), id={'type': 'dynamic-button', 'index': i}, value=i,
                                style={**btn_basic, **btn_style}, selected_style={**btn_basic, **btn_selected_style}))
                else:
                    status = 1
                    buttons.append(
                        dcc.Tab(label='M' + str(i), id={'type': 'dynamic-button', 'index': i}, value=i, disabled=True,
                                style={**btn_basic, **btn_style}, selected_style={**btn_basic, **btn_selected_style},
                                disabled_style={**btn_basic, **btn_disabled_style}))
            return [status, project_data['filename'], project_data['config'],
                    html.Div([dcc.Tabs(id='buttons', value=model_ix, children=buttons)], style={'width': '200vw'}),
                    tabs_style, btn_slider, btn_slider]
        else:
            for i in models:
                if models[i] == 'F':
                    if model_ix == '':
                        model_ix = i
                    buttons.append({'label': 'MODEL ' + str(i), 'value': i})
                else:
                    status = 1
                    buttons.append({'label': 'MODEL ' + str(i), 'value': i, 'disabled': True})

            return [status, project_data['filename'], project_data['config'],
                    dcc.Dropdown(id='buttons', options=buttons, value=model_ix, 
                        placeholder='Select Model', style={'width': '20vw'}),
                    {'width': '20vw', 'vertical-align': 'middle', 'margin-left': '4.5vw'},
                    {'display': 'none'}, {'display': 'none'}]
    else:
        ix = list(models.keys())[0]
        if models[ix] == 'F':
            model_ix = ix
        else:
            status = 1
        return [status, project_data['filename'], project_data['config'],
                html.Div([html.Button('M' + str(model_ix), id='buttons', value=model_ix,
                     style={**btn_basic, **btn_selected_style, 'border': '1px solid gray'})], style={'width': '20vw'}), 
                tabs_style, {'display': 'none'}, {'display': 'none'}]


@app.callback(Output("interval", "disabled"), [Input("interval_status", "value")])
def toggle_interval(status):
    if status == 0:
        return True
    else:
        raise PreventUpdate


@app.expanded_callback([Output('model-ix', 'value'), Output('model-data', 'data')], 
                       [Input('buttons', 'value')], 
                       [State('model-ix', 'value'), State('input-pk', 'value')])
def select_model(btn, ix, pk, **kwargs):

    if btn != '' and btn != ix:
        model_data = json.loads(views.project_data_model(kwargs['request'],pk,btn).getvalue().decode())	#dict of keys: 'model_index', 'dir', 'status', 'info', 'logs', 'error'
        matrix = struct = hbonds = ''
        try:
            media_path = Path(model_data['dir']).parent.absolute()
            if media_path.is_dir():
                try:
                    s = str(media_path)+"/matrix"+str(btn)+".npy"
                    if Path(s).is_file():
                        matrix = s
                except FileNotFoundError:
                    pass
                try:
                    s = str(media_path)+"/data"+str(btn)+".csv"
                    if Path(s).is_file():
                        struct = s
                except FileNotFoundError:
                    pass
                try:
                    s = str(media_path)+"/hbonds"+str(btn)+".csv"
                    if Path(s).is_file():
                        hbonds = s
                except FileNotFoundError:
                    pass
        except FileNotFoundError:
            pass

        return [btn, {'info': model_data['info'], 'matrix': matrix, 'struct': struct, 'hbonds': hbonds}]
    else:
        raise PreventUpdate


@app.expanded_callback([Output('con-intra', 'data'), Output('con-inter', 'data'), Output('contacts', 'data')],
                       [Input('model-ix', 'value')],
                       [State('model-data', 'data'), State('config', 'data'), State('pdb-code', 'data'),
                        State('con-intra', 'data'), State('con-inter', 'data'), State('contacts', 'data')])
def load_basic_data(ix, model_data, config, pdb_code, intra, inter, contacts):

    if model_data != '':
        if len(contacts) == 3 and pdb_code+"-"+str(ix) == contacts[2]:
            raise PreventUpdate
        else:
            info = model_data['info']['labels']  # dict = {'protein-A':[['AA:200','AA:201', ...],[from:to]]}
            matrix = np.load(model_data['matrix'])
            options1 = {}
            options2 = {}
            objects = []
            contacts = np.zeros(shape=(len(info), len(info)), dtype=int)

            n = len(info)
            for num1, i in enumerate(info):
                objects.append(i)
                r1 = info[i][1]  # range1
                for num2, j in enumerate(info):
                    if num2 >= num1:
                        r2 = info[j][1]  # range2
                        mat = matrix[r1[0]:r1[1], r2[0]:r2[1]]
                        mat = mat[np.nonzero(mat)]
                        counts = 0
                        try:
                            counts = len(mat[mat <= config["contact_cutoff"]])
                            if counts > 0:
                                if num1 == num2:
                                    val = i + ":" + str(r1[0]) + ":" + str(r1[1]) + ":" + str(counts)
                                    options1[i] = val
                                else:
                                    val = i + ":" + str(r1[0]) + ":" + str(r1[1]) + "|" + j + ":" + str(r2[0]) + ":" + \
                                          str(r2[1]) + "|" + str(counts)
                                    options2[i + ":" + j] = val
                        except ValueError:
                            pass
                        contacts[num1][num2] = counts
                        contacts[num2][num1] = counts
            return [options1, options2, [objects, contacts, pdb_code+"-"+str(ix)]]
    else:
        raise PreventUpdate


@app.expanded_callback(Output('data_1d', 'data'), 
                      [Input('model-ix', 'value')], 
                      [State('model-data', 'data'), State('pdb-code', 'data'), State('data_1d', 'data')])
def calc_1d_data(ix, model_data, pdb_code, data_prev):

    if model_data != '':
        try:
            if data_prev != '' and pdb_code+"-"+str(ix) == data_prev['hash']:
                raise PreventUpdate
        except ValueError:
            pass
        else:
            info = model_data['info']['labels']
            struct = pd.DataFrame()
            if model_data['struct'] != '':
                struct = pd.read_csv(model_data['struct'], sep = ',', engine = 'python')
            data_1d = {'hash': pdb_code+"-"+str(ix)}
            for i in info:
                if i.startswith('protein'):
                    residues = list(j.split(':')[0] for j in info[i][0])
                    patterns = calc_patterns(residues)
                    for z in patterns:
                        data_1d[i + ':' + z] = patterns[z]
                    data_1d[i + ':SEQ entropy'] = calc_entropy(residues)
                    if not struct.empty:
                        struct_data = struct[struct.chain == i.split('-')[1]]
                        if not struct_data.empty:
                            data_1d[i + ':II-structure'], data_1d[i + ':solvent access'] = calc_struct(info[i][0], struct_data)
                        else:
                            data_1d[i + ':II-structure'] = ''
                            data_1d[i + ':solvent access'] = ''
            return data_1d
    else:
        raise PreventUpdate


@app.expanded_callback([Output('1dx', 'options'), Output('1dy', 'options')], 
                       [Input('selected', 'value')],
                       [State('data_1d', 'data')])
def disable_1d_options(selected, data_1d):
    opts_a = []
    opts_b = []
    obj_a, obj_b = get_objects_in_contact(selected)

    if obj_a.startswith('protein'):
        if len(data_1d[obj_a + ':II-structure']):
            opts_a=[{'label': i, 'value': i, 'disabled': False} for i in opt_1D]
        else:
            opts_a=[{'label': i, 'value': i, 'disabled': True} if i in ['II-structure', 'solvent access'] else {'label': i, 'value': i, 'disabled': False} for i in opt_1D]
    else:
        opts_a=[{'label': i, 'value': i, 'disabled': True} for i in opt_1D]

    if obj_b.startswith('protein'):
        if len(data_1d[obj_b + ':II-structure']):
            opts_b=[{'label': i, 'value': i, 'disabled': False} for i in opt_1D]
        else:
            opts_b=[{'label': i, 'value': i, 'disabled': True} if i in ['II-structure', 'solvent access'] else {'label': i, 'value': i, 'disabled': False} for i in opt_1D]
    else:
        opts_b=[{'label': i, 'value': i, 'disabled': True} for i in opt_1D]

    return [opts_b, opts_a]


@app.callback([Output('settings', 'children'), Output('tabs', 'children')],
              [Input('tab-1', 'n_clicks'), Input('tab-2', 'n_clicks'), Input('tab-3', 'n_clicks'),
               Input('con-intra', 'data'), Input('con-inter', 'data')], 
              [State('selected', 'value'), State('model-data', 'data'), State('config', 'data')])
def identify_objects_in_contact_and_render_content(tab1, tab2, tab3, intra, inter, selected, model_data, config):
    tab = 'tab-1'
    ctx = dash.callback_context.triggered
    if len(ctx):
        tmp = ctx[0]['prop_id'].split('.')[0]
        if tmp.startswith('tab'):
            tab = tmp
    if tab == 'tab-1':
        return [
            html.Div([
                html.Div([
                    html.Label('to see Intramolecular Map', style=lab_style, title=title['intra-map']),
                    dcc.Dropdown(id='object_selected', placeholder="Select Object", clearable=False, optionHeight=30,
                                 options=[{'label': i, 'value': intra[i]} for i in intra], value='', style={'marginTop': '6px'})], 
                    style={**drops, 'marginLeft': '0.5vw', 'width': '20vw'}),
                html.Div([
                    html.Label('to see Intermolecular Map', style=lab_style, title=title['inter-map']),
                    dcc.Dropdown(id='interaction_selected', placeholder="Select Interaction", clearable=False,
                                 optionHeight=30, options=[{'label': i, 'value': inter[i]} for i in inter], value='', style={'marginTop': '6px'})],
                    style={**drops, 'width': '20vw'}),
                html.Div(
                    [html.P('or hover & click on either end of the selected ribbon',
                            style={**lab_style, 'color': 'gray', 'text-align': 'left', })],
                    style={'width': '40vw', 'display': 'block', 'vertical-align': 'bottom', 'marginLeft': '0.5vw'}, ),
            ], id='settings_chord'),
            html.Div([
                html.Div(id='dashbio-circos', style={'height': '90vh', 'width': '94vw', 'margin': '1vh 0 0 3vw'}),
                dcc.Input(id='click-data', type='hidden'),
                dcc.Input(id='chains-colors', type='hidden'),
            ])]

    elif tab == 'tab-2' and selected != '':
        if len(selected.split('|')) > 1:
            opts = [{'label': 'CM: contact map', 'value': 'C'}, {'label': 'DM: distance map', 'value': 'D'}]
            val = 'C'
            opt_cs=[{'label': i, 'value': colors_binary[i]} for i in colors_binary]
        else:
            opts = [{'label': 'CM|DM', 'value': 'M'}, {'label': 'CM: contact map', 'value': 'C'},
                    {'label': 'DM: distance map', 'value': 'D'}]
            val = 'M'
            opt_cs=[{'label': i, 'value': i} for i in colors]
        return [
            html.Div([
                html.Div([
                  html.Div([
                    html.Label('Basic options:', style={**lab_style, 'display':'block', 'color': 'rgb(149, 165, 166)', 'margin-bottom': '1vh', 'margin-left':'0.5vw', 'font-size': '2vh'}, title=title['basic_opts']),
                    html.Div([
                        html.Label('Display Mode', style=lab_style, title=title['display-mode']),
                        dcc.Dropdown(id='display_mode', placeholder="Select mode", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=opts, value=val)],
                        style={**drops, 'marginLeft': '0.5vw', 'width': '20vw'}),
                    html.Div([
                        html.Label('Cutoff [Å]', style=lab_style, title=title['cutoff']),
                        dcc.Input(id="cutoff", type="number", placeholder=" default: 8Å", min=0, value=config["contact_cutoff"], step=0.1,
                                  debounce=False,
                                  style=dict(height='29px', width='10vw', marginTop='6px', color='dimgrey', display='block',
                                             borderRadius='5px 5px 5px 5px', borderColor='rgba(0,0,0,0)'))],
                        style={**drops, 'vertical-align': 'top', 'width': '18vw', 'margin-right': '1vw'}, ),
                    ], style={'display':'block'}, ),
                    html.Div([
                        html.Label('ColorScale', style=lab_style, title=title['color-scale']),
                        dcc.Dropdown(id='color_selected', placeholder="Select Color", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=opt_cs, value=opt_cs[0]['value'])],
                        style={**drops, 'marginLeft': '0.5vw', 'width': '18vw',}, ),
                    html.Div([
                        html.Label('Reverse', id='check-reverse', style=lab_style, title=title['reverse-cs']),
                        dcc.Checklist(id='reverse', options=[{'label': '', 'value': '_r'}, ], value='', ), ],
                        style={'width': '22vw', 'marginTop': '3vh', 'marginLeft': '2vw', 'display': 'inline-block',
                               'vertical-align': 'top'}, ),

                    html.Hr(style={'border-top': '1px solid lightgray', 'margin': '0.7vw 0.5vw 0.7vw 0.5vw'}),
                    html.Label('Filter contacts:', style={**lab_style, 'display':'block', 'color': 'rgb(149, 165, 166)', 'margin-bottom': '1vh', 'margin-left':'0.5vw', 'font-size': '2vh'}, title=title['filters']),
                    html.Div([
                        html.Label('intra-Contact Filter', id='intra_contact', style=lab_style, title=title['intra-filter']),
                        dcc.Input(id="filter_cutoff", type="number", placeholder=" i, i+n: n=0", min=0, value=0, step=1,
                                  debounce=False,
                                  style=dict(height='29px', width='10vw', marginTop='6px', color='dimgrey',
                                             borderRadius='5px 5px 5px 5px', borderColor='rgba(0,0,0,0)')),
                        html.Label(' i, i+n', style={'font-style': 'italic', 'color': '#95A5A6'})],
                        style={**drops, 'vertical-align': 'top', 'width': '18vw', 'marginLeft': '0.5vw', 'margin-right': '1vw'}, ),
                    html.Div([
                        html.Label('Interaction Filter', style=lab_style, title=title['interaction-filter']),
                        dcc.Dropdown(id='feature_selected', placeholder="Select Feature", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=[
                                         {'label': 'filter: none', 'value': 'none', 'disabled': False},
                                         {'label': 'hydropathy', 'value': 'hydropathy', 'disabled': False, 'title': title['hydropathy']},
                                         {'label': 'hydrophobic', 'value': 'hydrophobic', 'disabled': False, 'title': title['hydrophobic']},
                                         {'label': 'hydrophilic', 'value':  'hydrophilic', 'disabled': False, 'title': title['hydrophilic']},
                                         {'label': 'electrostatics', 'value': 'electrostatics', 'disabled': False, 'title': title['electrostatics']},
                                         {'label': 'π-π stacking', 'value': 'π-π stacking', 'disabled': False, 'title': title['pi-stacking']},
                                         {'label': 'π-ion stacking', 'value': 'π-ion stacking', 'disabled': False, 'title': title['ion-stacking']},
                                         {'label': 'hydrogen bonds', 'value': 'hydrogen bonds', 'disabled': False, 'title': title['hbonds']},
                                     ], value='none')],
                        style={**drops, 'width': '18vw', 'marginLeft': '1vw'}),
                    html.Div([
                        html.Label('Only', id='filter-only', style=lab_style, title=title['interaction-only']),
                        dcc.Checklist(id='filter', options=[{'label': '', 'value': 'only'}, ], value='', ), ],
                        style={'width': '4vw', 'marginTop': '3vh', 'marginLeft': '0.8vw', 'display': 'inline-block',
                               'vertical-align': 'top'}, ),

                    html.Hr(style={'border-top': '1px solid lightgray', 'margin': '0.7vw 0.5vw 0.7vw 0.5vw'}),
                    html.Label('Display 1D data along sequence:', style={**lab_style, 'display':'block', 'color': 'rgb(149, 165, 166)', 'margin-bottom': '1vh', 'margin-left':'0.5vw', 'font-size': '2vh'}, title=title['features']),
                    html.Div([
                        html.Div([
                            html.Label('Select Y-axis Feature', style=lab_style, title=title['feature-y']),
                            dcc.Dropdown(id='1dy', placeholder="Select 1D Feature", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=[{'label': i, 'value': i, 'disabled': False} for i in opt_1D], value='none')],
                            style={**drops, 'width': '18vw', 'marginLeft': '0.5vw'}, ),
                        html.Div([
                            html.Label('Select X-axis Feature', style=lab_style, title=title['feature-x']),
                            dcc.Dropdown(id='1dx', placeholder="Select 1D Feature", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=[{'label': i, 'value': i, 'disabled': False} for i in opt_1D], value='none')],
                            style={**drops, 'width': '18vw'}),
                    ], style={'display': 'block'}),

                    html.Hr(style={'border-top': '1px solid lightgray', 'margin': '0.7vw 0.5vw 0.7vw 0.5vw'}),
                    html.Label('Change the chart title:', style={**lab_style, 'display':'block', 'color': 'rgb(149, 165, 166)', 'margin-bottom': '1vh', 'margin-left':'0.5vw', 'font-size': '2vh'}, title=title['title']),
                    dcc.Input(id="map-title", type="text", placeholder="Provide new title", debounce=False, value='',
                            style=dict(height='29px', width='40vw', margin='6px 0 1vh 0.5vw', color='dimgrey',
                                borderRadius='5px 5px 5px 5px', borderColor='rgba(0,0,0,0)')),
                ]),
            ], id='settings_map'),

            html.Div([
                html.Div([
                    dcc.Loading(id='loading-map', type='circle',
                            children=[html.Div(dcc.Graph(id='graph_map',
                                                         style={'height': '94vh', 'width': '95vw', 'margin-top': '0',
                                                                'margin-left': '4vw'},
                                                         config={'responsive': True,
                                                                 'modeBarButtonsToAdd':['drawline', 'drawopenpath',
                                                                     'drawclosedpath', 'drawcircle', 'drawrect',
                                                                     'eraseshape', 'resetViews', 'toggleHover', 'toggleSpikelines'],
                                                             'toImageButtonOptions': {'format': 'svg', 'width': 1400,
                                                                     'filename': 'mapiya.svg', 'height': 1000, 'scale': 1.5}}))]),
                ], className='graph-parent'),
                dcc.Input(id='click-map', type='hidden'),
            # return info of clicked point on the map;
            ])]

    elif tab == 'tab-3':
        return [
            html.Div([], id='settings_download'),

            html.Div([
                html.Div(id='text-output'),
            ])]
    else:
        raise PreventUpdate


@app.expanded_callback([Output('feature_selected', 'options'), Output('hbonds', 'value')], 
                        Input('model-data', 'data'), 
                        State('feature_selected', 'options'))
def update_filter_options(model_data, options):
    path_hb = model_data['hbonds']
    options[-1]['disabled'] = True
    if path_hb != '':
        hbonds = pd.read_csv(path_hb, sep = ',', engine = 'python')
        if len(hbonds) > 0:
            options[-1]['disabled'] = False
    return [options, path_hb]


@app.expanded_callback([Output('color_selected', 'options'), Output('color_selected', 'value'), Output('check-reverse', 'children')], 
                        Input('display_mode', 'value'))
def update_cs(mode):
    if mode == 'C':
        S = html.Label('Smoth CS', style=lab_style, title=title['smoth-cs'])
        return [[{'label': i, 'value': colors_binary[i]} for i in colors_binary], colors_binary['Silver'], S]
    else:
        R = html.Label('Reverse', style=lab_style, title=title['reverse-cs'])
        return [[{'label': i, 'value': i} for i in colors], colors[0], R]


@app.expanded_callback([Output('dashbio-circos', 'children'), Output('chains-colors', 'value')], Input('contacts', 'data'))
def display_circos(data):
    if not len(data):
        raise PreventUpdate
    labels = data[0]
    contacts = data[1]
    matrix = normalize_contact_counts(contacts)
    radii_sribb = [0.3] * len(labels)
    ideo_colors = ['rgba(186,225,255,0.9)', 'rgba(186,255,201,0.9)', 'rgba(255,255,186,0.9)',
                   'rgba(255,223,186,0.9)', 'rgba(224,194,143,0.9)', 'rgba(255,154,130,0.9)',
                   'rgba(255,179,186,0.9)', 'rgba(209, 135, 135,0.9)', 'rgba(184,161,177,0.9)',
                   'rgba(211,195,181,0.9)', ]  # pink, orange, yellow, green, blue, purple, brown, gray

    k = len(labels) / len(ideo_colors)
    if k > 1:
        new_colors = []
        for i in range(int(k) + 1):
            new_colors.extend(ideo_colors)
        ideo_colors = new_colors

    chains_colors = {i:ideo_colors[n] for n, i in enumerate(labels)}

    shapes = []
    ideograms = []
    ribbon_info = []

    layout = go.Layout(title='', plot_bgcolor='#FFFFFF',
                       showlegend=False, margin=dict(t=20, b=0, l=0, r=0),
                       xaxis=dict(range=[-1.4, 1.4], gridcolor='rgba(0,0,0,0)', zeroline=False, tickmode='array',
                                  tickvals=[0], ticktext=[''], scaleanchor = "y", scaleratio = 1,),
                       yaxis=dict(range=[-1.15, 1.15], gridcolor='rgba(0,0,0,0)', zeroline=False, tickmode='array',
                                  tickvals=[0], ticktext=[''], ),
                       )
    shapes, ideograms, ribbon_info = make_shapes_and_info(matrix, contacts, labels, ideo_colors, radii_sribb)
    layout['shapes'] = shapes
    ideograms.extend(ribbon_info)
    fig = go.Figure(data=ideograms, layout=layout)

    return [dcc.Graph(id='graph-circos', figure=fig, config={'responsive':True}, style={'height':'78vw', 'margin-top': '0',}), json.dumps(chains_colors, indent=2)]


@app.expanded_callback(Output('click-data', 'value'), Input('graph-circos', 'clickData'))
def display_click_data(data):
    if data is not None:
        data = data["points"][0]
        if 'text' in data:
            data = data['text'].split()
            if len(data) == 5 and data[3].startswith('intra'):
                data = data[0]
            elif len(data) == 7 and data[3].startswith('inter'):
                data = data[0] + ':' + data[6]
        return data
    else:
        return ''


@app.expanded_callback([Output('tab-2', 'n_clicks'), Output('selected', 'value')],
                       [Input('buttons', 'value'), Input('click-data', 'value'),
                        Input('object_selected', 'value'), Input('interaction_selected', 'value')],
                       [State('con-intra', 'data'), State('con-inter', 'data'), State('tab-2', 'n_clicks')])
def switch_to_map_tab(btn, click, obj, interaction, intra, inter, n):
    if n is None:
        n = 0
    ctx = dash.callback_context.triggered
    if len(ctx):
        ctx = ctx[0]['prop_id'].split('.')[0]
    if ctx == 'buttons':
        return [0, '']
    elif obj != '':
        return [n + 1, str(obj)]
    elif interaction != '':
        return [n + 1, str(interaction)]
    elif click != '' and click is not None:
        if len(str(click).split(':')) == 1:
            return [n + 1, intra[click]]
        else:
            if click in inter:
                return [n + 1, inter[click]]
            else:
                click = click.split(':')
                return [n + 1, inter[click[1] + ':' + click[0]]]
    else:
        raise PreventUpdate


@app.expanded_callback([Output('tab-2', 'style'), Output('intra_contact', 'style'), Output('filter_cutoff', 'disabled')], 
                       [Input('selected', 'value')], [State('tab-2', 'style')])
def disable_map_button(selected, style):
    if selected == '':
        return [{**style, 'color': '#95A5A6'}, {**lab_style, 'color': '#95A5A6'}, True]
    elif len(selected.split('|')) > 1:
        return [{**style, 'color': '#63533c'}, {**lab_style, 'color': '#95A5A6'}, True]
    else:
        return [{**style, 'color': '#63533c'}, lab_style, False]


@app.expanded_callback([Output('opts', 'style'), Output('opts', 'disabled'), Output('settings-dir', 'style')], 
                       [Input('tab-1', 'n_clicks'), Input('tab-2', 'n_clicks'), Input('tab-3', 'n_clicks')], 
                       [State('opts', 'style'), State('settings-dir', 'style')])
def disable_opts_button(tab1, tab2, tab3, opts, style):
    ctx = dash.callback_context.triggered
    if len(ctx):
        ctx = ctx[0]['prop_id'].split('.')[0]
    if ctx == 'tab-3':
        return [{**opts, 'color': '#95A5A6'}, True, {**style, 'display': 'none'}]
    else:
        return [{**opts, 'color': '#63533c'}, False, {**style, 'display': 'block'}]


@app.expanded_callback(Output('colors_1d', 'data'),
                      [Input('1dy', 'value'), Input('1dx', 'value')],
                      [State('selected', 'value'), State('data_1d', 'data'), State('colors_1d', 'data')])
def prepare_colors_for_1d_params(param_y, param_x, selected, data_1d, prev_colors):
    
    obj_a, obj_b = get_objects_in_contact(selected)
    param_x = param_x.replace('_n', '')
    param_y = param_y.replace('_n', '')
    hash_x = obj_b+":"+param_x
    hash_y = obj_a+":"+param_y
    mol_colors = {'x': '', 'y': ''}
    if param_y != "none" and obj_a.startswith('protein'):
        prev = ''
        try:
            prev = prev_colors['y'][0]
        except:
            pass
        if prev != hash_y:
            cs = params[param_y][0]
            cs_a = np.array([i[0] for i in cs])
            mol_colors['y'] = [hash_y, [cs[np.abs(cs_a - float(val)).argmin()][1] for val in data_1d[hash_y]]]
        else:
            try:
                mol_colors['y'] = prev_colors['y']
            except:
                pass

    if param_x != "none" and obj_b.startswith('protein'):
        prev = ''
        try:
            prev = prev_colors['x'][0]
        except:
            pass
        if prev != hash_x:
            cs = params[param_x][0]
            cs_a = np.array([i[0] for i in cs])
            mol_colors['x'] = [hash_x, [cs[np.abs(cs_a - float(val)).argmin()][1] for val in data_1d[hash_x]]]
        else:
            try:
                mol_colors['x'] = prev_colors['x']
            except:
                pass
    return mol_colors


@app.expanded_callback(Output('data_Dist', 'data'),
                      Input('selected', 'value'),
                      State('model-data', 'data'))
def prepare_distance_data(selected, model_data):
    if selected == '':
        raise PreventUpdate
    else:
        path_matrix = model_data['matrix']
        res_list = model_data['info']['labels']

        selected = selected.split('|')
        obj_a = selected[0].split(':')
        obj_b = obj_a
        if len(selected) > 1:
            obj_b = selected[1].split(':')

        residues_a = res_list[obj_a[0]][0]
        residues_b = res_list[obj_b[0]][0]

        desc_d = np.load(path_matrix)[int(obj_a[1]):int(obj_a[2]), int(obj_b[1]):int(obj_b[2])].round(decimals=3)

        data_dist = [desc_d, residues_a, residues_b, obj_a, obj_b]
        return data_dist


@app.expanded_callback(Output('data_Con', 'data'), 
                      [Input('cutoff', 'value'), Input('data_Dist', 'data'), Input('hbonds', 'value'),
                       Input('display_mode', 'value'), Input('feature_selected', 'value'), Input('filter_cutoff', 'value')])
def prepare_contact_data(cutoff, data_dist, hbonds, mode, feature, intra_n):
    distances = np.array(data_dist[0])
    residues_a = [i.split(':')[0] for i in data_dist[1]]
    residues_b = [i.split(':')[0] for i in data_dist[2]]
    obj_a_type = data_dist[3][0].split('-')[0]
    obj_b_type = data_dist[4][0].split('-')[0]

    desc_c = np.zeros(distances.shape, 'U500')
    filtrated = np.zeros(distances.shape, 'U10')
    if cutoff == '':
        cutoff = 8.0

    maxi = np.amax(distances)
    is_intra = False
    if data_dist[3] == data_dist[4]:
        is_intra = True
        np.fill_diagonal(distances, maxi)
        if intra_n != None and intra_n > 0:
            for i in range(1,intra_n+1):
                np.fill_diagonal(distances[i:], maxi)
                np.fill_diagonal(distances[:,i:], maxi)

    if feature == 'hydrogen bonds':
        hbonds = pd.read_csv(hbonds, sep = ',', engine = 'python')
#        if data_dist[3][0].startswith('protein') and data_dist[4][0].startswith('protein'):
        if obj_a_type == 'protein' and obj_b_type == 'protein':
            donor = data_dist[3][0].split('-')[1]
            accep = data_dist[4][0].split('-')[1]
            ch_hb = hbonds[hbonds.chains == donor+':'+accep]
            if len(ch_hb) > 0:
                is_hb = True
                hbonds = ch_hb
                donor_set = data_dist[1]
                accep_set = data_dist[2]
            else:
                ch_hb = hbonds[hbonds.chains == accep+':'+donor]
                if len(ch_hb) > 0:
                    is_hb = True
                    hbonds = ch_hb
                    donor = accep
                    accep = data_dist[3][0].split('-')[1]
                    donor_set = data_dist[2]
                    accep_set = data_dist[1]
                else:
                    is_hb = False
        else:
           is_hb = False

    desc_c[distances > cutoff] = 'NO'
    for (x,y) in zip(*np.where(desc_c != 'NO')):
        hb_desc = ''
        interaction = 'YES<br>'
        if obj_a_type in ['protein', 'nucleic'] and obj_b_type in ['protein', 'nucleic']:
            interaction = calc_contact_nature(residues_a[x], residues_b[y])
        if feature == 'hydrogen bonds':
            if is_hb:
                hb = hbonds[(hbonds.donor == donor_set[x]) & (hbonds.acceptor == accep_set[y])]
                if len(hb) > 0:
                    filtrated[x][y] = 0.1
                    hb_desc = ' calculated by EDHB:<br>'+'<br>'.join(['HB-type: '+row['type'].upper()+
                              ', '+row['proton']+' in '+donor+':'+row['donor']+'  &  '+row['acc_atom']+' in '+accep+':'+
                              row['acceptor']+', length: '+str(row['length']) for index, row in hb.iterrows()])
                else:
                    filtrated[x][y] = '-'
            else:
                filtrated[x][y] = '-'
        else:
            filtrated[x][y] = filter_contact_by_nature(residues_a[x], residues_b[y], feature)
        if filtrated[x][y] != '-':
            interaction += 'interaction filter: '+feature+hb_desc
        desc_c[x][y] = interaction
        if is_intra:
            filtrated[y][x] = filtrated[x][y]
            desc_c[y][x] = desc_c[x][y]

    map_label = 'DISTANCE MAP'
    if mode == 'M':
        contacts = np.copy(distances)
        contacts[contacts <= cutoff] = cutoff - 1
        contacts[contacts > cutoff] = maxi
        contacts = np.tril(contacts, -1)
        m = np.nonzero(contacts)
        contacts[contacts == cutoff - 1] = round(maxi / 3, 2)
        distances[m] = contacts[m]
        map_label = 'CM / DM'
    elif mode == 'C':
        distances[distances > cutoff] = cutoff + 0.1
        distances[distances == 0] = cutoff + 0.1
        map_label = 'CONTACT MAP'

    data_con = [distances, desc_c, cutoff, filtrated, CS_CONTACT[feature], map_label]
    return data_con


@app.expanded_callback(Output('colors_con', 'data'),
                      [Input('data_Con', 'data'), Input('color_selected', 'value')],
                      [State('data_Dist', 'data'), State('display_mode', 'value'), State('cutoff', 'value')])
def prepare_colors_for_contacts(data_con, cs_con, data_dist, mode, cutoff):
    
    obj_a = data_dist[3][0]
    obj_b = data_dist[4][0]
    residues_a = data_dist[1]
    residues_b = data_dist[2]
    contacts = np.array(data_con[0])
    if mode != 'C':
        cs_con = 'rgb(128,128,0)'
    filtrated = cs = cs_a = ''
    try:
        filtrated = np.array(data_con[3])
        cs = data_con[4][0]
        cs_a = np.array([i[0] for i in cs])
    except:
        pass

    is_intra = False
    if obj_a == obj_b:
        is_intra = True

    values = {'objects' : obj_a+":"+obj_b}
    colors = {}
    for ni, i in enumerate(residues_a):
        is_valid = True
        for nj, j in enumerate(residues_b):
            if is_intra == True and nj > ni:
                is_valid = False
            if contacts[ni][nj] < cutoff and is_valid == True:
                colors[i+"-"+j] = cs_con
                if cs != '':
                    val = '-'
                    try:
                        val = float(filtrated[ni][nj])
                    except:
                        pass
                    if val != '-':
                        colors[i+"-"+j] = cs[np.abs(cs_a - float(val)).argmin()][1]
    values['contacts'] = colors
    return values



@app.expanded_callback(Output('graph_map', 'figure'),
                       [Input('feature_selected', 'value'), Input('color_selected', 'value'), Input('reverse', 'value'),
                        Input('1dy', 'value'), Input('1dx', 'value'), Input('data_1d', 'data'),
                        Input('data_Dist', 'data'), Input('data_Con', 'data'),
                        Input('feature_selected', 'value'), Input('filter', 'value'), Input('map-title', 'value')],
                        State('pdb-code', 'data'))
def display_contact_map(feature, cs, rv, y_val, x_val, data_1d, data_dist, data_con, filtr, only, desc_title, pdb_name):
    if len(pdb_name) > 10:
        pdb_name = pdb_name[:11]

    distances = data_con[0]
    desc_c = data_con[1]
    cutoff = data_con[2]
    map_label = data_con[5]
    desc_d = data_dist[0]
    residues_a = data_dist[1]
    residues_b = data_dist[2]
    obj_a = data_dist[3]
    obj_b = data_dist[4]
    cf = cutoff
    sc_len = 0.5

    if len(rv) > 0 and rv[0] == '_r':
        if cs.startswith('rgb'):
            cs = [[0, cs], [0.999, '#F8F8F8'], [1, 'rgba(255,255,255, 0.0)']]
            cf = cutoff - 0.5
            sc_len = 0.12
        else:
            cs = cs + rv[0]
    elif cs.startswith('rgb'):
        cs = [[0, cs], [0.999, cs], [1, 'rgba(255,255,255, 0.0)']]
        cf = cutoff/2
        sc_len = 0.12

    dataset = []
    ax = 0.96
    if x_val != 'none':
        ax = 0.88

    sc_show = True
    shift = 0.0
    sc_x = 0.98
    sc_y = 0.98
    if y_val != 'none':
        sc_x = sc_y - params[y_val][2]
    if y_val == 'composition' or x_val == 'composition':
        shift = 0.02
    if y_val != 'none' or x_val != 'none':
        sc_len = 0.12
        if y_val == x_val:
            sc_show = False

        if y_val != 'none':
            base = 0
            cmax = 0.99
            desc_y = ['' for i in residues_a]
            if y_val != 'hydropathy_n':
                color = list(map(float, data_1d[obj_a[0] + ':' + y_val]))
                x_vals = [1] * len(residues_a)
                if y_val == 'SEQ entropy':
                    x_vals = color
                    desc_y = ['Shannon entropy: '+str(i) for i in color]
                    cmax = np.amax(color)
                    params[y_val][3] = [0.1, cmax - 0.1]
                    params[y_val][4] = ['0.00', str(cmax)]
                elif y_val == 'solvent access':
                    x_vals = color
                    desc_y = ['RSA: '+str(i) for i in color]
                elif y_val == 'hydropathy':
                    desc_y = ['Kyte-Doolittle: '+str(round((i*9)-4.5,1)) for i in color]
                    x_vals = [x - 0.5 for x in color]
                    base = 0.5
            elif y_val == 'hydropathy_n':
                color = list(map(float, data_1d[obj_a[0] + ':hydropathy']))
                desc_y = ['normalized K-D: '+str((i)) for i in color]
                x_vals = color
            trace2 = go.Bar(x=x_vals, y=residues_a, orientation='h', base=base, text=desc_y,
                            name=y_val + '<br>' + obj_a[0], hoverlabel=dict(namelength=-1),
                            hovertemplate='residue: %{y} in ' + obj_a[0] + '<br>%{text}',
                            marker=dict(cmin=0.00, cmax=cmax, color=color, colorscale=params[y_val][0], showscale=True,
                                        colorbar=dict(title=params[y_val][1], len=params[y_val][2], x=1, y=sc_y - shift,
                                                      yanchor="top", tickvals=params[y_val][3],
                                                      ticktext=params[y_val][4]), ), showlegend=False, yaxis='y1',
                            xaxis='x2')
            dataset.append(trace2)

        if x_val != 'none':
            base = 0
            cmax = 0.99
            desc_x = ['' for i in residues_a]
            if x_val != 'hydropathy_n':
                color = list(map(float, data_1d[obj_b[0] + ':' + x_val]))
                y_vals = [1] * len(residues_b)
                if x_val == 'SEQ entropy':
                    y_vals = color
                    desc_x = ['Shannon entropy: '+str(i) for i in color]
                    cmax = np.amax(color)
                    params[x_val][3] = [0.1, cmax - 0.1]
                    params[x_val][4] = ['0.00', str(cmax)]
                elif x_val == 'solvent access':
                    y_vals = color
                    desc_x = ['RSA: '+str(i) for i in color]
                elif x_val == 'hydropathy':
                    desc_x = ['Kyte-Doolittle: '+str(round((i*9)-4.5, 1)) for i in color]
                    y_vals = [x - 0.5 for x in color]
                    base = 0.5
            elif x_val == 'hydropathy_n':
                color = list(map(float, data_1d[obj_b[0] + ':hydropathy']))
                desc_x = ['normalized K-D: '+str(i) for i in color]
                y_vals = color
            trace3 = go.Bar(x=residues_b, y=y_vals, text=desc_x, base=base, name=x_val + '<br>' + obj_b[0],
                            hoverlabel=dict(namelength=-1),
                            hovertemplate='residue: %{x} in ' + obj_b[0] + '<br>%{text}',
                            marker=dict(cmin=0.00, cmax=cmax, color=color, colorscale=params[x_val][0],
                                        showscale=sc_show,
                                        colorbar=dict(title=params[x_val][1], len=params[x_val][2], x=1, y=sc_x,
                                                      yanchor="top", tickvals=params[x_val][3],
                                                      ticktext=params[x_val][4]), ), showlegend=False, yaxis='y2',
                            xaxis='x1')

            dataset.append(trace3)
    if len(only) == 0 or filtr == 'none':
        trace1 = go.Heatmap(x=residues_b, y=residues_a, z=distances, name=map_label, colorscale=cs, yaxis='y1',
                        xaxis='x1', text=desc_c, hovertext=desc_d,
                        hovertemplate='residue: %{x} in ' + obj_b[0] + '<br>residue: %{y} in ' + obj_a[0] + 
                                      '<br>distance: %{hovertext} [Å]<br>contact cutoff: ' + str(cutoff) + 
                                      ' [Å]<br>contact: %{text}',
                        colorbar=dict(title='CONTACTS', len=sc_len, x=1, y=-0.02, yanchor="bottom",
                                     tickmode='array', tickvals=[cf], ticktext=['cutoff='+str(cutoff)]))
        dataset.append(trace1)
    if filtr != 'none':
        cs_tmp = data_con[4]
        trace4 = go.Heatmap(x=residues_b, y=residues_a, z=data_con[3], zmin=0, zmax=1, name='filter',
                                                yaxis='y1', xaxis='x1', text=desc_c, hovertext=desc_d,
                        hovertemplate='residue: %{x} in ' + obj_b[0] + '<br>residue: %{y} in ' + obj_a[0] + 
                                      '<br>distance: %{hovertext} [Å]<br>contact cutoff: ' + str(cutoff) + 
                                      ' [Å]<br>contact: %{text}',
                        colorscale=cs_tmp[0],
                        colorbar=dict(title=cs_tmp[1], len=cs_tmp[2], x=1, y=sc_len - (2 * shift), yanchor="bottom",
                                      tickmode='array', tickvals=cs_tmp[3], ticktext=cs_tmp[4]),)
        dataset.append(trace4)

    if desc_title == '':
        desc_title = "PDB: " + pdb_name + ", Contact Map between objects: " + obj_a[0] + " and " + obj_b[0]

    return {
        'data': dataset,
        'layout': go.Layout(
            title={'text': desc_title,
                   'y': 0.99, 'x': 0.43,
                   'xanchor': 'center', 'yanchor': 'top'},
            title_font=dict(size=16, color="gray"),
            paper_bgcolor='rgba(0,0,0,0)',
            autosize=True,
            hovermode='closest',
            xaxis1=dict(tickfont=dict(size=17), title=dict(text=obj_b[0], font=dict(color="black", size=24)),
                        automargin=True, domain=[0, 0.87], range=[-1, int(obj_b[2]) - int(obj_b[1]) + 1], tickangle=45,
                        showline=True),
            xaxis2=dict(tickfont=dict(size=18, color="gray"), automargin=True, domain=[0.87, 0.955], tickmode='array',
                        tickvals=[0.5], ticktext=[y_val + '-' + obj_a[0].split('-')[1]], tickangle=45),
            yaxis1=dict(tickfont=dict(size=16), title=dict(text=obj_a[0], font=dict(color="black", size=24)),
                        domain=[0, ax], range=[-0.9, int(obj_a[2]) - int(obj_a[1]) + 1], tickangle=0, showline=True,
                        automargin=True),
            yaxis2=dict(tickfont=dict(size=16, color="gray"), tickmode='array', tickvals=[0.5],
                        ticktext=[x_val + '-' + obj_b[0].split('-')[1]], domain=[0.88, 0.965], showline=False,
                        automargin=True),
            margin=dict(t=0),
        )
    }


@app.expanded_callback(Output('click-map', 'value'), 
                       Input('graph_map', 'clickData'), 
                       State('selected', 'value'))
def display_click_map(data, selected):
    ctx = dash.callback_context.triggered
    if len(ctx):
        ctx = ctx[0]['prop_id'].split('.')[0]
        if ctx == 'graph_map':
            selected = selected.split('|')
            res2 = selected[0].split(':')[0].split('-')[1]
            res1 = res2
            if len(selected) > 1:
                res1 = selected[1].split(':')[0].split('-')[1]
            data = data['points'][0]
            return json.dumps({'res1' : res1+'-'+data['x'].replace(':', '-'), 
                               'res2' : res2+'-'+data['y'].replace(':', '-')}, indent=2)
    else:
        raise PreventUpdate



@app.expanded_callback([Output('text-output', 'children')], 
                       [Input('selected', 'value')],
                       [State('model-data', 'data'), State('data_Con', 'data'), State('config', 'data')])
def load_download_section(selected, model_data, data_con, config):

    keys = list(config.keys())
    cutoff = str(config[keys[0]])
    if len(data_con) == 6:
        cutoff = str(data_con[2])
    path = model_data['matrix'].split('matrix')
    model = str(path[1].split('.')[0])
    path = path[0]
    files = {'fixed':'model'+model+'.pdb', 'envir':'environment'+model+'.pdb', 'struct':'data'+model+'.csv', 'hbonds':'hbonds'+model+'.csv', 'pqr':'model'+model+'.pqr', 'elec':'model'+model+'.dx'}
    status = {'fixed': False, 'envir': False, 'struct': False, 'hbonds': False, 'pqr': False, 'elec': False, 'display': False}
    for i in files.keys():
        my_file = Path(path+files[i])
        if not my_file.is_file():
            status[i] = True
    is_con = ""
    display = "contacts"
    if selected is None or selected == '':
        is_con = "True"
#        status['display'] = True
        display = "counts"
    opts = ["matrix of contact counts|counts|", "contact list from current map|contacts|"+is_con, 
            "Shannon Entropy for map objects|entropy|"+is_con, "Physicochemical properties|patterns|"+is_con, "Sequence in FASTA format|seq|"]

    return [
        html.Div([
            html.P('The Mapiya analysis for model '+model+' was performed with the following settings:', style={**lab_style, 'font-size': '2.5vh', 'margin': '1vh 0 1vh 0'}),
            html.Table([
                html.Tr([
                    html.Td(keys[0]+': '+cutoff, style={'width': '25vh'}),
                    html.Td(keys[2]+': '+str(config[keys[2]]), style={'width': '25vh'}),
                    html.Td(keys[6]+': '+str(config[keys[6]]), style={'width': '25vh'}),
                ]),
                html.Tr([
                    html.Td(keys[1]+': '+str(config[keys[1]]), style={'width': '25vh'}),
                    html.Td(keys[3]+': '+str(config[keys[3]]), style={'width': '25vh'}),
                    html.Td(keys[4]+': '+str(config[keys[4]]), style={'width': '25vh'}),
                    html.Td(keys[5]+': '+str(config[keys[5]]), style={'width': '25vh'}),
                ]),
                html.Tr([
                    html.Td(keys[8]+': '+str(config[keys[8]]), style={'width': '25vh'}),
                    html.Td(keys[9]+': '+str(config[keys[9]]), style={'width': '25vh'}),
                    html.Td(keys[10]+': '+str(config[keys[10]]), style={'width': '25vh'}),
                    html.Td(keys[11]+': '+str(config[keys[11]]), style={'width': '25vh'}),
                ]),
                html.Tr([
                    html.Td(keys[12]+': '+str(config[keys[12]]), style={'width': '25vh'}),
                    html.Td(keys[13]+': '+str(config[keys[13]]), style={'width': '25vh'}),
                    html.Td(keys[14]+': '+str(config[keys[14]]), style={'width': '25vh'}),
                    html.Td(keys[15]+': '+str(config[keys[15]]), style={'width': '25vh'}),
                ]),
                html.Tr([
                    html.Td(keys[7]+': '+str(config[keys[7]]), style={'width': '25vh'}),
                ]),
            ], style={'font-size': '2vh', 'margin-bottom': '2vh', 'color': 'gray'}),


            html.P('Please download the results:', style={**lab_style, 'font-size': '2.5vh', 'margin': '1vh 0 2vh 0'}),
            dcc.Download(id="download-file"),
            html.Div([
                html.Button("FIXED PDB", id="btn_fixed", value="PDB", disabled=status['fixed'], style={'min-width': '100px'}),
                html.P('PDB fixed with PDBFixer', style={'font-size': '2vh', 'margin': '0 0 1vh 1vw', 'display': 'inline-block', 'align': 'center'}),
            ]),
            html.Div([
                html.Button("FIXED PDB", id="btn_envir", disabled=status['envir'], style={'min-width': '100px'}),
                html.P('PDB fixed with PDBFixer; environment added', style={'font-size': '2vh', 'margin': '0 0 1vh 1vw', 'display': 'inline-block', 'align': 'center'}),
            ]),
            html.Div([
                html.Button("DATA CSV", id="btn_struct", disabled=status['struct'], style={'min-width': '100px'}),
                html.P('Structural properties calculated with STRIDE', style={'font-size': '2vh', 'margin': '0 0 1vh 1vw', 'display': 'inline-block', 'align': 'center'}),
            ]),
            html.Div([
                html.Button("DATA CSV", id="btn_hbonds", disabled=status['hbonds'], style={'min-width': '100px'}),
                html.P('Hydrogen Bonds calculated with EDHB', style={'font-size': '2vh', 'margin': '0 0 1vh 1vw', 'display': 'inline-block', 'align': 'center'}),
            ]),
            html.Div([
                html.Button("DATA PQR", id="btn_pqr", disabled=status['pqr'], style={'min-width': '100px'}),
                html.P('Electrostatics: partial charges calculated with APBS', style={'font-size': '2vh', 'margin': '0 0 1vh 1vw', 'display': 'inline-block', 'align': 'center'}),
            ]),
            html.Div([
                html.Button("DATA DX", id="btn_elec", disabled=status['elec'], style={'min-width': '100px'}),
                html.P('Electrostatics: electrostatic potential calculated with APBS', style={'font-size': '2vh', 'margin': '0 0 1vh 1vw', 'display': 'inline-block', 'align': 'center'}),
            ]),

            dcc.Download(id="download-txt"),
            html.P('or display the other datasets:', style={**lab_style, 'font-size': '2.5vh', 'margin': '2vh 0 0vh 0'}),
            html.Div([
                dcc.Dropdown(id='display_data', placeholder="Select dataset", clearable=False,
                    style={'width': '30vw', 'margin-right': '2vw', 'display': 'inline-block'}, optionHeight=30,
                    options=[{'label': i.split('|')[0], 'value': i.split('|')[1], 'disabled': bool(i.split('|')[2])} for i in opts], value=display),
                html.Button("DATA TXT", id="btn_display", disabled=status['display'], style={'min-width': '100px', 'display': 'inline-block'}),
                html.P('Custom dataset provided in TXT format', style={'font-size': '2vh', 'margin': '0 0 0 1vw', 'display': 'inline-block'}),
            ], style={**drops, 'width': '80vw', 'margin': '1vh 0 1vh 0', 'display': 'flex', 'align-items': 'center'}),
            html.Div(id='textarea', style={'width': '90vw', 'height': 250, 'margin-top': '0'}, ),
        ], style={'width': '90vw', 'margin-top': '0', 'margin-left': '5vw'}),
    ]


@app.callback([Output('textarea', 'children'), Output('download-text', 'value')], 
              [Input('display_data', 'value')], 
              [State('selected', 'value'), State('model-data', 'data'), 
               State('contacts', 'data'), State('data_Con', 'data'), State('data_1d', 'data')])
def display_the_datasets(display, selected, model_data, counts, dist, data_1d):

    if display == 'counts':
        keys = counts[0].copy()
        keys.insert(0, ' ')
        vals = counts[1]
        text = ','.join(keys)+'\n'
        for n,i in enumerate(vals):
            i.insert(0, counts[0][n])
            text += ','.join(str(j) for j in i)+'\n'
        return [
            [html.Table(
                [html.Tr([html.Td(i, style={'min-width': '10vw', 'padding-left': '1vw'}) for i in keys], style={'background-color':'#eeece7'})] +
                [html.Tr([html.Td(i, style={'min-width': '10vw', 'padding-left': '1vw'}) for i in j]) for j in vals]
            )],
            [text, display]
        ]

    else:
        labels = model_data['info']['labels']
        objA = selected.split('|')[0].split(':')[0]
        objB = objA
        objects = [objA]
        if len(selected.split('|')) > 1:
            objB = selected.split('|')[1].split(':')[0]
            objects.append(objB)
        if display == 'contacts':
            residuesA = labels[objA][0]
            residuesB = labels[objB][0]
            con = np.array(dist[1])
            distance = np.array(dist[0])
            text = objA.rjust(10)+' '+objB.rjust(10)+'  distance  possible_interaction_forces\n'
            for (x,y) in zip(*np.where(con != 'NO')):
                text += residuesA[x].rjust(10)+' '+residuesB[y].rjust(10)+'  '+str(distance[x][y]).rjust(8)+'  '+con[x][y].replace('YES<br>possible interaction forces:<br>- ','').replace('<br>','').replace('- ','')+'\n'
            return [[dcc.Textarea(value='{}'.format(text), style={'width': '90vw', 'height': 250, 'margin-top': '0'}, ),], [text, display]]

        if display == 'entropy':
            text = ''
            for z in objects:
                if z+':SEQ entropy' in data_1d:
                    entropy = data_1d[z+':SEQ entropy']
                    text += '> '+z+'\n'+'residue'.rjust(8)+'  '+'Entropy'.rjust(6)+'\n'
                    for n, i in enumerate(labels[z][0]):
                        text += i.rjust(8)+'  '+str(entropy[n]).rjust(6)+'\n'
                    text += '\n'

            return [[dcc.Textarea(value='{}'.format(text), style={'width': '90vw', 'height': 250, 'margin-top': '0'}, ),], [text, display]]

        if display == 'patterns':
            text = ''
            for z in objects:
                if z.startswith('protein'):
                    text += '> '+z+' [0-NO, 1-YES]'+'\n'+' residue hydrophobic amphipatic hydrophilic HB_donor HB_acceptor polar charged aromatic\n'
                    for n, i in enumerate(labels[z][0]):
                        text += i.rjust(8)+'  '
                        res = i.split(':')[0]
                        for feature in ['hydrophobic', 'amphipatic', 'hydrophilic', 'H-Bond donor', 'H-Bond acceptor', 'polar']:
                            if res in PATTERNS[feature]:
                                text += '1  '
                            else:
                                text += '0  '
                        if res in PATTERNS['charged'][0]:
                            text += '+  '
                        elif res in PATTERNS['charged'][1]:
                            text += '-  '
                        else:
                            text += '0  '
                        if res in PATTERNS['aromatic']:
                            text += '⌬   '
                        elif res in PATTERNS['π-bond']:
                            text += 'π  '
                        else:
                            text += '0  '
                        text += '\n'
                    text += '\n'

            return [[dcc.Textarea(value='{}'.format(text), style={'width': '90vw', 'height': 250, 'margin-top': '0'}, ),], [text, display]]

        if display == 'seq':
            text = ''
            for i in labels.keys():
                if i.startswith('protein'):
                    text += '> '+i+' : length='+str(labels[i][1][1]-labels[i][1][0])+'\n'
                    text += ''.join([A_CODE[j.split(':')[0]] for j in labels[i][0]])+'\n\n'
                elif i.startswith('nucleic'):
                    text += '> '+i+' : length='+str(labels[i][1][1]-labels[i][1][0])+'\n'
                    text += ''.join([N_CODE[j.split(':')[0]] for j in labels[i][0]])+'\n\n'

            return [[dcc.Textarea(value='{}'.format(text), style={'width': '90vw', 'height': 250, 'margin-top': '0'}, ),], [text, display]]

        else:
            return ['', ['', '']]


@app.callback(Output("download-file", "data"), 
             [Input("btn_fixed", "n_clicks"), Input("btn_envir", "n_clicks"),
              Input("btn_struct", "n_clicks"), Input("btn_hbonds", "n_clicks"), 
              Input("btn_pqr", "n_clicks"), Input("btn_elec", "n_clicks")], 
              State('model-data', 'data'), prevent_initial_call=True)
def download_the_results(fixed, envir, struct, hbonds, pqr, elec, model_data):

    path = model_data['matrix']
    ctx = dash.callback_context
    button = ctx.triggered[0]['prop_id'].split('.')[0]
    if button == 'btn_fixed':
        return dcc.send_file(path.replace('matrix', 'model').replace('npy', 'pdb'))
    elif button == 'btn_envir':
        return dcc.send_file(path.replace('matrix', 'environment').replace('npy', 'pdb'))
    elif button == 'btn_struct':
        return dcc.send_file(model_data['struct'])
    elif button == 'btn_hbonds':
        return dcc.send_file(model_data['hbonds'])
    elif button == 'btn_pqr':
        return dcc.send_file(path.replace('matrix', 'model').replace('npy', 'pqr'))
    elif button == 'btn_elec':
        return dcc.send_file(path.replace('matrix', 'model').replace('npy', 'dx'))


@app.callback(Output("download-txt", "data"), 
              Input("btn_display", "n_clicks"), 
              State("download-text", "value"), prevent_initial_call=True)
def download_display(display, text):
    ctx = dash.callback_context
    button = ctx.triggered[0]['prop_id'].split('.')[0]
    if button == 'btn_display':
        return dict(content=text[0], filename="Mapiya_data_"+text[1]+".txt")
    else:
        raise PreventUpdate


