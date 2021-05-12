import os
import json
import numpy as np
import math
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash

from .models import Map, MapModel

# CSS style
tab_style = {'margin': '0 0.5vw 0.5vh 0.5vw', 'background-color': '#95C8D8', 'padding': '0.5vh 0', 'color': 'gray', 'font-size': '2vh'}
tab_disabled_style = {'margin': '0 0.5vw 0.5vh 0.5vw', 'background-color': '#f5f5f0', 'padding': '0.5vh 0', 'color': '#bfbfbf', 'font-size': '2vh'}
tab_selected_style = {'margin': '0 0.5vw 0.5vh 0.5vw', 'borderBottom': '3px solid #4682B4', 'background-color': '#95C8D8', 'padding': '0.5vh 0', 'color': 'black', 'font-size': '2vh'}
labs = {'margin': '0 0','color': 'gray', 'text-align': 'left', 'font-size': '1.8vh'}
drops = {'margin': '0 0 0.4vh 0.5vw','width': '20vw', 'display': 'inline-block', 'font-size': '2vh', 'font-family': 'Ubuntu, sans-serif', 'color':'dimgrey'}
lab_style = {'color': 'white', 'text-align': 'left', 'font-size': '0.85rem', 'font-weight': '500', 'margin-left':'2px', 'font-family': 'Ubuntu, sans-serif'}
drop_style = {'margin': '1vh 0 0 2vw','width': '13vw', 'display': 'inline-block', 'font-size': '2vh', 'color': 'dimgrey', 'font-family': 'Ubuntu, sans-serif'}

# colorscales
colors = ['Viridis', 'Cividis', 'Inferno', 'Magma', 'Plasma', 'Turbo', 'Blackbody', 'Blured', 'Electric', 'Hot', 'Jet', 'Rainbow', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdBu', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'turbid', 'thermal', 'haline', 'solar', 'ice', 'gray', 'deep', 'dense', 'algae', 'matter', 'speed', 'amp', 'tempo', 'Burg', 'Burgyl', 'Redor', 'Oryel', 'Peach', 'Pinkyl', 'Mint', 'Blugrn', 'Darkmint', 'Emrld', 'Aggrnyl', 'Bluyl', 'Teal', 'Tealgrn', 'Purp', 'Purpor', 'Sunset', 'Magenta', 'Sunsetdark', 'Agsunset', 'Brwnyl']
cs_seq = [[0, "#c6ff1a"], [0.05, "#c6ff1a"], [0.05, "#ffff00"], [0.1, "#ffff00"], [0.1, "#ffcc00"], [0.15, "#ffcc00"], [0.15, "#ff944d"], [0.2, "#ff944d"], [0.2,"#ff6600"], [0.25,"#ff6600"], [0.25, "#e62e00"], [0.3, "#e62e00"], [0.3, "#cc0000"], [0.35, "#cc0000"], [0.35, "#b30059"], [0.4, "#b30059"], [0.4, "#ff0080"], [0.45, "#ff0080"], [0.45, "#ff00ff"], [0.5, "#ff00ff"], [0.5, "#bf00ff"], [0.55, "#bf00ff"], [0.55, "#8000ff"], [0.6, "#8000ff"], [0.6, "#262673"], [0.65, "#262673"], [0.65, "#4000ff"], [0.7, "#4000ff"], [0.7, "#0080ff"], [0.75, "#0080ff"], [0.75, "#00bfff"], [0.8, "#00bfff"], [0.8, "#00ffff"], [0.85, "#00ffff"], [0.85, "#00e6ac"], [0.9, "#00e6ac"], [0.9, "#009900"], [0.95, "#009900"], [0.95, "#004d00"], [0.999, "#004d00"], [1, "#cccccc"]]
cs_binary = [[0, '#ffffff'], [0.49, '#ffffff'], [0.5, '#1DACD6'], [1, '#1DACD6']]
cs_ternary = [[0, 'rgb(255,255,255)'], [0.33, 'rgb(255,255,255)'], [0.33, "#1DACD6"], [0.66, "#1DACD6"], [0.66, "#000066"], [0.99, "#000066"], [1, '#cccccc']]

# colorhash
acids={'-': 1, 'X': 1, 'TRP': 0, 'PHE': 0.05, 'TYR': 0.1, 'ASN': 0.15, 'GLN': 0.2, 'ASP': 0.25, 'GLU': 0.3, 'SER': 0.35, 'THR': 0.4, 'HIS': 0.45, 'LYS': 0.5, 'ARG': 0.55, 'LEU': 0.6, 'ILE': 0.65, 'VAL': 0.7, 'ALA': 0.75, 'GLY': 0.8, 'MET': 0.85, 'CYS': 0.9, 'PRO': 0.95}
K_D_normal={'ALA':0.70,'ARG':0.00,'ASN':0.11,'ASP':0.11,'CYS':0.78,'GLN':0.11,'GLU':0.11,'GLY':0.46,'HIS':0.14,'ILE':1.00,'LEU':0.92,'LYS':0.07,'MET':0.71,'PHE':0.81,'PRO':0.32,'SER':0.41,'THR':0.42,'TRP':0.40,'TYR':0.36,'VAL':0.97}


# const. data
amino = ['W', 'F', 'Y', 'N', 'Q', 'D', 'E', 'S', 'T', 'H', 'K', 'R', 'L', 'I', 'V', 'A', 'G', 'M', 'C', 'P']
AA = {'ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL'}
K_D = {'ALA':'1.8','ARG':'-4.5','ASN':'-3.5','ASP':'-3.5','CYS':'2.5','GLN':'-3.5','GLU':'-3.5','GLY':'-0.4','HIS':'-3.2','ILE':'4.5','LEU':'3.8','LYS':'-3.9','MET':'1.9','PHE':'2.8','PRO':'-1.6','SER':'-0.8','THR':'-0.7','TRP':'-0.9','TYR':'-1.3','VAL':'4.2'}

params = {'composition': [cs_seq, 'SEQUENCE', 0.45, [0.02, 0.07, 0.12, 0.17, 0.22, 0.27, 0.32, 0.37, 0.42, 0.47, 0.52, 0.57, 0.62, 0.67, 0.72, 0.77, 0.82, 0.87, 0.92, 0.97], amino],
          'hydropathy': ['RdBu', 'HYDROPATHY', 0.22, [0.1, 0.5, 0.9], ['-4.5 (philic)','0.0','4.5 (phobic)']],
          'hydropathy_n': ['RdBu', 'HYDROPATHY<br>(normalized)', 0.22, [0.1, 0.5, 0.9], ['0 (philic)','0.5','1 (phobic)']],
          'hydrophobic': [cs_binary, 'HYDROPHOBIC', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'amphipatic':  [cs_binary, 'AMPHIPATIC', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'hydrophilic': [cs_binary, 'HYDROPHILIC', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'charged':  [cs_ternary, 'CHARGE', 0.25, [0.17,0.5,0.83], ['NO', 'positive', 'negative']],
          'polar':  [cs_binary, 'POLAR', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'nonpolar':  [cs_binary, 'NONPOLAR', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'aromatic':  [cs_binary, 'AROMATIC', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'π-bond':  [cs_binary, 'non-aromatic<br>π-BOND', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'sulfur':  [cs_ternary, 'SULFUR', 0.25, [0.17, 0.5, 0.83], ['NO', 'CYS', 'MET']],
          'H-Bond donor': [cs_binary, 'H-BOND DONOR', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'H-Bond acceptor': [cs_binary, 'H-BOND ACCEPTOR', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'SEQ entropy': ['GnBu', 'ENTROPY', 0.22, [], []],
}
opt_1D = ['none', 'composition', 'hydropathy', 'hydropathy_n', 'hydrophobic', 'amphipatic', 'hydrophilic', 'charged', 'polar', 'nonpolar', 'aromatic', 'π-bond', 'sulfur', 'H-Bond donor', 'H-Bond acceptor', 'electrostatics', 'SEQ entropy', 'II-structure', 'solvent access']

app = DjangoDash('ContactMap')
app.css.append_css({'external_url': '/static/css/app.css'})

app.layout = html.Div([
    dcc.Input(id="input-pk", value='', type='hidden'),		# current object pk
    dcc.Input(id="matrix", value='', type='hidden'),		# path to distance matrix NxN
    dcc.Input(id="residues", value='', type='hidden'),		# residues dict = {'object':['AA:ix', 'AA:ix', ...]}
    dcc.Input(id="objects", value='', type='hidden'),		# objects dict = {'id':[from, to, type-chain]}
    dcc.Input(id="contacts", value='', type='hidden'),		# contacts matrix[id1][id2] = 0 or 1 (if 2 objects in contact)
    dcc.Input(id="selected", value='', type='hidden'),		# selected object or interaction
    dcc.Input(id="data_1D", value='', type='hidden'),		# dict of features for 1D plots

    dcc.Tabs(id='tabs-list', value='tab-1', parent_className='custom-tabs', className='custom-tabs-container', 
        children=[
        dcc.Tab(label='OBJECTS & INTERACTIONS', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='CONTACT MAP', value='tab-2', style=tab_style, selected_style=tab_selected_style, disabled=True, disabled_style=tab_disabled_style),
        dcc.Tab(label='DOWNLOAD DATA', value='tab-3', style=tab_style, selected_style=tab_selected_style),
    ], colors={"border": "1px solid rgba(0,0,0,1)", "background": "rgba(0,0,0,0.1)",},),
    html.Div(id='tabs', style={'height':'88vh'}),
], style={'height':'97vh', 'width':'96vw', 'margin':'0', 'padding':'0'})


@app.expanded_callback([Output('matrix', 'value'), Output('residues', 'value'), Output('objects', 'value'), Output('contacts', 'value')], [Input('input-pk', 'value')])
def load_basic_data(pk):

    model = MapModel.objects.get(map_id=pk)
    info = json.loads(model.info)

    objects = {}
    ix_from = 0
    for num, key in enumerate(info):
      length = len(info[key])
      objects[str(num)] = [ix_from, ix_from+length-1, key]
      ix_from += length

    matrix = np.load(os.getcwd()+model.matrix.url)
    n=len(objects)
    contacts = np.zeros(shape=(n,n), dtype = int)
    for obj1 in range(0,n):
      i = objects[str(obj1)]
      for obj2 in range(obj1,n):
        j = objects[str(obj2)]
        mat = matrix[i[0]:i[1]+1, j[0]:j[1]+1]
        try:
          mini = np.amin(mat[np.nonzero(mat)])
          if mini < 8.0:
            contacts[obj1][obj2]=1
            contacts[obj2][obj1]=1
        except ValueError:  #raised if mat[np.nonzero(mat)] is empty.
          pass
    return [str(os.getcwd()+model.matrix.url), str(info), str(objects), str(contacts)]


@app.callback(Output('tabs', 'children'), [Input('tabs-list', 'value'), Input('objects', 'value'), Input('contacts', 'value')])
def identify_objects_in_contact_and_render_content(tab, obj, con):

    if tab == 'tab-1':
        options1=[]
        options2=[]
        objects = json.loads(obj.replace('\'', '\"'))
        contacts = json.loads(con.replace(' ', ','))
        for num,i in enumerate(objects):
          if contacts[num][num] == 1:
            label = str(objects[i][2])
            val = label+':'+str(objects[i][0])+":"+str(objects[i][1])
            options1.append({'label': label, 'value': val})
          for j in range(num, len(objects)):
            if num != j and contacts[num][j] == 1:
              label = str(objects[i][2]+':'+objects[str(j)][2])
              val = str(objects[i][2]+':'+str(objects[i][0])+":"+str(objects[i][1])+'|'+objects[str(j)][2]+":"+str(objects[str(j)][0])+":"+str(objects[str(j)][1]))
              options2.append({'label': label, 'value': val})

        return html.Div([
            html.Div([
              html.Div([
                html.Label('Intermolecular Map', style=labs),
                dcc.Dropdown(id='object_selected', placeholder="Select Object", clearable=False, optionHeight = 30,
                  options=options1, value='')], style=drops,),
              html.Div([
                html.Label('Intramolecular Map', style=labs),
                dcc.Dropdown(id='interaction_selected', placeholder="Select Interaction", clearable=False, optionHeight = 30,
                  options=options2, value='')], style={**drops, 'margin-left': '2.5vw'},),
            ]),
            html.Div([
                dcc.Loading(id='loading-chord', children=[html.Div(dcc.Graph(id='graph_chord', style={'height': '80vh'}, 
            config={'toImageButtonOptions': {'format':'svg', 'width':1200, 'height':1200, 'scale':1}, 'responsive': True}, ))], type='circle'),
            ], className='graph-parent'),
        ])

    elif tab == 'tab-2':
        return html.Div([
            html.Div([
            html.Div([
              html.Div([
                html.Label('Select Contact Filter', style=lab_style),
                dcc.Dropdown(id='feature_selected', placeholder="Select Feature", clearable=False, style={'margin-top':'6px'}, optionHeight = 30,
                  options=[
                    {'label': 'distance cutoff', 'value': 'D'},
                    {'label': 'interaction types', 'value': 'H'},
                    {'label': 'filter: hydrophobic', 'value': 'H'},
                    {'label': 'filter: polar', 'value': 'P'},
                    {'label': 'filter: charged', 'value': 'E'},
                    {'label': 'filter: aromatic', 'value': 'A'},
                  ], 
                  value='D')], style={**drop_style, 'margin-left':'1vw', 'width':'17vw'} ),
              html.Div([
                html.Label('Select ColorScale', style=lab_style),
                dcc.Dropdown(id='color_selected', placeholder="Select Color", clearable=False, style={'margin-top':'6px'}, optionHeight = 30,
                  options=[{'label': i, 'value': i} for i in colors])], style=drop_style, ),
              html.Div([
                html.Label('Reverse', style=lab_style),
                dcc.Checklist(id='reverse', options=[{'label': '', 'value': '_r'},], value='',),], 
                  style={'width': '6vw', 'marginTop':'3.5vh', 'marginLeft': '0.8vw', 'display': 'inline-block', 'vertical-align':'top'}, ),
              html.Div([
                html.Label('Select Cutoff [Å]', style=lab_style),
                dcc.Input(id="cutoff", type="number", placeholder=" default: 8Å", min=0, value='', step=0.1, debounce=True, 
                  style=dict(height='29px', width='13vw', marginTop='6px', borderRadius= '5px 5px 5px 5px', borderColor='rgba(0,0,0,0)', color='dimgrey'))],
                style={**drop_style, 'vertical-align':'top', 'width':'12vw', 'margin-right': '2vw'}, ),
              html.Div([
                html.Label('Select 1D-Y', style=lab_style),
                dcc.Dropdown(id='1dy', placeholder="Select 1D Feature", clearable=False, style={'margin-top':'6px'}, optionHeight = 30,
                  options=[{'label': i, 'value': i} for i in opt_1D], value='none')], style={**drop_style, 'width':'17.5vw'}, ),
              html.Div([
                html.Label('Select 1D-X', style=lab_style),
                dcc.Dropdown(id='1dx', placeholder="Select 1D Feature", clearable=False, style={'margin-top':'6px'}, optionHeight = 30,
                  options=[{'label': i, 'value': i} for i in opt_1D], value='none')], style={**drop_style, 'width':'17.5vw'}, ),
            ], className="content"),
            ], className="hoverable"),

            html.Div([
                dcc.Loading(id='loading-map', children=[html.Div(dcc.Graph(id='graph_map', style={'height': '94vh', 'margin-top': '0'}, 
            config={'toImageButtonOptions': {'format':'svg', 'width':1400, 'height':800, 'scale':1.5}, 'responsive': True}, ))], type='circle'),
            ], className='graph-parent'),
        ])

    elif tab == 'tab-3':
        return html.Div([
            html.Div([
              html.Div([
                html.Label('Some options_1', style=labs),
                dcc.Dropdown(id='options1', placeholder="Select ...", clearable=False, optionHeight = 30,
                  options=[{'label': 'H bonds', 'value': 'HB'}, {'label': 'interactions', 'value': 'I'},], value='')], style=drops,),
              html.Div([
                html.Label('Some options_2', style=labs),
                dcc.Dropdown(id='options2', placeholder="Select ...", clearable=False, optionHeight = 30,
                  options=[], value='')], style={**drops, 'margin-left': '2.5vw'},),
            ]),
            dcc.Textarea(id='textarea', value='Textarea content initialized\nwith multiple lines of text', style={'width': '100%', 'height': 300, 'margin-top': '5px'},),
            html.Div(id='text-output'),
        ])


@app.expanded_callback([Output('text-output', 'children')], [Input('textarea', 'value'), Input('data1D', 'value'), Input('options1', 'value')])
def load_download_section(text, dat, val):

    return ['You have entered: \n{}'.format(text)]


@app.expanded_callback(Output('graph_chord', 'figure'), [Input('objects', 'value'), Input('interaction_selected', 'options')])
def display_chord(obj_all, obj_con):

    objects = json.loads(obj_all.replace('\'', '\"'))

    fig = go.Figure()

    return fig


@app.expanded_callback([Output('tabs-list', 'value'), Output('selected', 'value')], [Input('object_selected', 'value'), Input('interaction_selected', 'value')])
def switch_to_map_tab(obj, interaction):
    if obj != '':
      return ['tab-2', str(obj)]
    elif interaction != '':
      return ['tab-2', str(interaction)]
    else:
      raise PreventUpdate


@app.expanded_callback(Output('color_selected', 'value'), [Input('selected', 'value')])
def switch_color(sel):
    if len(sel.split('|')) == 1:
      return 'ice'
    else:
      return 'Blues'


@app.expanded_callback(Output('data_1D', 'value'), Input('residues', 'value'))
def calc_1D_data(resids):
    
    data_1D = {}
    res_list = json.loads(resids.replace('\'', '\"'))
    for i in res_list:
      if i.startswith('protein'):
        residues = list(i.split(':')[0] for i in res_list[i])
        data_1D[i+':composition'] = list(acids[i] for i in residues)
        data_1D[i+':hydropathy'] = list(K_D_normal[i] for i in residues)
        s_len = len(residues)
        entropy = [0]*s_len
        for z in ['hydrophobic', 'amphipatic', 'hydrophilic', 'charged', 'polar', 'nonpolar', 'aromatic', 'π-bond', 'sulfur', 'H-Bond donor', 'H-Bond acceptor', 'SEQ entropy']:
          data_1D[i+':'+z] = ['0']*s_len
        for n, j in enumerate(residues):
          if j in ['ALA', 'GLY', 'LEU', 'ILE', 'VAL', 'PRO', 'PHE']:			# hydrophobic
            data_1D[i+':hydrophobic'][n] = '0.7'
          if j in ['TRP', 'TYR', 'MET', 'LYS']:						# amphipatic
            data_1D[i+':amphipatic'][n] = '0.7'
          if j in ['ARG', 'ASN', 'ASP', 'GLN', 'GLU', 'HIS', 'SER', 'THR', 'CYS']:	# hydrophilic
            data_1D[i+':hydrophilic'][n] = '0.7'
          if j in ['LYS', 'ARG', 'HIS']:						# charged-positive
            data_1D[i+':charged'][n] = '0.5'
          if j in ['GLU', 'ASP']:							# charged-negative
            data_1D[i+':charged'][n] = '0.8'
          if j in ['CYS', 'MET', 'SER', 'THR', 'TYR', 'GLN', 'ASN']:			# polar
            data_1D[i+':polar'][n] = '0.7'
          if j in ['ALA', 'GLY', 'ILE', 'LEU', 'VAL', 'PHE', 'PRO', 'TRP']:		# nonpolar
            data_1D[i+':nonpolar'][n] = '0.7'
          if j in ['PHE', 'TYR', 'TRP', 'HIS']:						# aromatic
            data_1D[i+':aromatic'][n] = '0.7'
          if j in ['ARG', 'ASN', 'ASP', 'GLN', 'GLU', 'GLY']:				# non-aromatic pi-system
            data_1D[i+':π-bond'][n] = '0.7'
          if j == 'CYS':								# sulfur containing: disulfide bridge
            data_1D[i+':sulfur'][n] = '0.8'
          elif j == 'MET':								# sulfur containing: S-π interactions
            data_1D[i+':sulfur'][n] = '0.5'
          if j in ['ARG', 'ASN', 'GLN', 'HIS', 'LYS', 'SER', 'THR', 'TRP', 'TYR']:	# hydrogen bond donor
            data_1D[i+':H-Bond donor'][n] = '0.7'
          if j in ['ASN', 'ASP', 'GLN', 'GLU', 'HIS', 'SER', 'THR', 'TYR']:		# hydrogen bond acceptor
            data_1D[i+':H-Bond acceptor'][n] = '0.7'

          if n <= s_len - 6:
            frag = residues[n:n+6]
            S = 0
            for kk in AA:
              gg = frag.count(kk)/6
              if gg > 0:
                S += gg*math.log2(gg)
            for z in range(n, n+6):
              entropy[z] += (S*(-1))/6
        data_1D[i+':SEQ entropy'] = ["%.2f" % number for number in entropy]
    return str(data_1D)

# 'electrostatics', 'II-structure', 'solvent access'

@app.expanded_callback(Output('graph_map', 'figure'), [Input('selected', 'value'), Input('feature_selected', 'value'), Input('color_selected', 'value'), Input('reverse', 'value'), Input('cutoff', 'value'), Input('matrix', 'value'), Input('residues', 'value'), Input('1dy', 'value'), Input('1dx', 'value'), Input('data_1D', 'value')])
def display_contact_map(selected, feature, cs, rv, cutoff, path_matrix, resids, y_val, x_val, data1D):

#    print('Start... ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))######
    if len(rv) > 0 and rv[0] == '_r':
      cs = cs+rv[0]
    objA = ''
    objB = ''
    tokens = selected.split('|')
    if len(tokens) == 1:
      objA = tokens[0].split(':')
      objB = objA
    else:
      objA = tokens[0].split(':')
      objB = tokens[1].split(':')

    res_list = json.loads(resids.replace('\'', '\"'))
    residuesA = res_list[objA[0]]
    residuesB = res_list[objB[0]]

    distances = np.load(path_matrix)[int(objA[1]):int(objA[2])+1, int(objB[1]):int(objB[2])+1].round(decimals=3)
    desc_d = np.copy(distances)
    desc_c = np.zeros(distances.shape, 'U3')
    if cutoff == '':
      cutoff = 8.1
    desc_c[desc_d < cutoff] = 'YES'
    desc_c[desc_d > cutoff] = 'NO'

    if objA == objB:
      maxi = np.amax(distances)
      contacts = np.copy(distances)
      contacts[contacts <= cutoff] = cutoff-1
      contacts[contacts > cutoff] = maxi
      contacts = np.tril(contacts,-1)
      m = np.nonzero(contacts)
      contacts[contacts == cutoff-1] = maxi/3
      distances[m] = contacts[m]
    else:
      distances[distances > cutoff] = 0

    dataset = []

    ax = 0.96
    if x_val != 'none':
      ax = 0.88
    y_ax1 = dict(tickfont = dict(size = 16), title = dict(text = objA[0], font=dict(color="black", size=24)), domain=[0, ax], 
        range=[-0.9, int(objA[2])-int(objA[1])+1], tickangle = 0, showline=True, automargin=True)

    sc_len = 0.975
    if y_val != 'none' or x_val != 'none':
      sc_len = 0.5
      data1D = json.loads(data1D.replace('\'', '\"'))

###---Colorbars position settings
      sc_show = True
      sc_x = 0.98
      sc_y = 0.53
      if y_val == 'composition' and x_val != 'none':
         sc_x = 0.53
         if x_val != y_val:
           if x_val == 'charged':
             sc_len = 0.28
           else:
             sc_len = 0.33
      elif x_val == 'composition' and y_val != 'none':
         if y_val != x_val:
           if y_val == 'charged':
             sc_y = 0.28
             sc_len = 0.28
           else:
             sc_y = 0.33
             sc_len = 0.33
      if y_val == x_val:
        sc_show = False

      if y_val != 'none':
        base = 0
        cmax = 0.99
        if y_val != 'hydropathy_n':
          color = list(map(float, data1D[objA[0]+':'+y_val]))
          x_vals = [1]*len(residuesA)
          if y_val == 'SEQ entropy':
            x_vals = color
            cmax = np.amax(color)
            params[y_val][3] = [0.1, cmax-0.1]
            params[y_val][4] = ['0.00', str(cmax)]
          if y_val == 'hydropathy':
            x_vals = [x - 0.5 for x in color]
            base = 0.5
        else:
          color = list(map(float, data1D[objA[0]+':hydropathy']))
          x_vals = color
        trace2 = go.Bar(x=x_vals, y=residuesA, orientation='h', base=base, text=residuesA, name=y_val+'<br>'+objA[0], hoverlabel=dict(namelength = -1), hoverinfo="text+name", 
          marker=dict(cmin=0.00, cmax=cmax, color=color, colorscale=params[y_val][0], showscale=True,
          colorbar=dict(title=params[y_val][1], len=params[y_val][2], x=1, y=sc_y, yanchor="bottom", tickvals=params[y_val][3], ticktext=params[y_val][4]),), showlegend=False, yaxis='y1', xaxis='x2')
        dataset.append(trace2)

      if x_val != 'none':
        base = 0
        cmax = 0.99
        if x_val != 'hydropathy_n':
          color = list(map(float, data1D[objB[0]+':'+x_val]))
          y_vals = [1]*len(residuesB)
          if x_val == 'SEQ entropy':
            y_vals = color
            cmax = np.amax(color)
            params[x_val][3] = [0.1, cmax-0.1]
            params[x_val][4] = ['0.00', str(cmax)]
          if x_val == 'hydropathy':
            y_vals = [x - 0.5 for x in color]
            base = 0.5
        else:
          color = list(map(float, data1D[objB[0]+':hydropathy']))
          y_vals = color
        trace3 = go.Bar(x=residuesB, y=y_vals, text=residuesB, base=base, name=x_val+'<br>'+objB[0], hoverlabel=dict(namelength = -1), hoverinfo="text+name", 
          marker=dict(cmin=0.00, cmax=cmax, color=color, colorscale=params[x_val][0], showscale=sc_show,
          colorbar=dict(title=params[x_val][1], len=params[x_val][2], x=1, y=sc_x, yanchor="top", tickvals=params[x_val][3], ticktext=params[x_val][4]),), showlegend=False, yaxis='y2', xaxis='x1')

        dataset.append(trace3)
    trace1 = go.Heatmap(x=residuesB, y=residuesA, z=distances, name='DISTANCE MAP', colorscale=cs, yaxis='y1', xaxis='x1', 
        text=desc_c, hovertext=desc_d, hovertemplate='residue: %{x} in '+objB[0]+'<br>residue: %{y} in '+objA[0]+'<br>distance: %{hovertext} [Å]<br>contact cutoff: '+str(cutoff)+' [Å]<br>contact: %{text}',
        colorbar=dict(title='DISTANCES', len=sc_len, x=1, y=0, yanchor="bottom"))
    dataset.append(trace1)
    return {
        'data': dataset,
        'layout': go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            autosize=True,
            hovermode='closest',
            xaxis1=dict(tickfont = dict(size = 17), title = dict(text = objB[0], font=dict(color="black", size=24)), automargin = True, domain=[0, 0.87], 
                   range=[-1, int(objB[2])-int(objB[1])+1], tickangle = 45, showline=True),
            xaxis2=dict(tickfont = dict(size = 18, color="gray"), automargin = True, domain=[0.87, 0.955],tickmode='array', tickvals=[0.5], ticktext=[y_val+'-'+objA[0].split('-')[1]],  tickangle = 45),
            yaxis1=y_ax1,
            yaxis2=dict(tickfont = dict(size = 16, color="gray"), tickmode='array', tickvals=[0.5], ticktext=[x_val+'-'+objB[0].split('-')[1]], domain=[0.88, 0.965], showline=False, automargin = True),
            margin=dict(t=0),
         )
    }
