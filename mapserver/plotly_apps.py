import os
import json
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash

# CSS style
tab_style = {'margin': '0 0.5vw 0.5vh 0.5vw', 'background-color': '#95C8D8', 'padding': '0.5vh 0', 'color': 'gray', 'font-size': '2vh'}
tab_disabled_style = {'margin': '0 0.5vw 0.5vh 0.5vw', 'background-color': '#f5f5f0', 'padding': '0.5vh 0', 'color': '#bfbfbf', 'font-size': '2vh'}
tab_selected_style = {'margin': '0 0.5vw 0.5vh 0.5vw', 'borderBottom': '3px solid #4682B4', 'background-color': '#95C8D8', 'padding': '0.5vh 0', 'color': 'black', 'font-size': '2vh'}
labs = {'margin': '0 0','color': 'gray', 'text-align': 'left', 'font-size': '1.8vh'}
drops = {'margin': '0 0 0.4vh 0.5vw','width': '20vw', 'display': 'inline-block', 'font-size': '2vh', 'font-family': 'Ubuntu, sans-serif', 'color':'dimgrey'}
lab_style = {'color': 'white', 'text-align': 'left', 'font-size': '0.85rem', 'font-weight': '500', 'margin-left':'2px', 'font-family': 'Ubuntu, sans-serif'}
drop_style = {'margin': '1vh 0 0 2.5vw','width': '14vw', 'display': 'inline-block', 'font-size': '2vh', 'color': 'dimgrey', 'font-family': 'Ubuntu, sans-serif'}

# colorscales
cs_blues = [[0, "#ffffff"], [0.05, "#f6fdff"], [0.10, "#e6f9ff"], [0.20, "#b4e6f4"], [0.3, "#82d2ea"], [0.4, "#1DACD6"], [0.5, "#1680ba"], [0.6, "#1060a5"], [0.7, "#0b4090"], [0.8, "#000066"], [0.9, "#000029"], [1, "rgb(0,0,0)"]]
colors = ['Viridis', 'Cividis', 'Inferno', 'Magma', 'Plasma', 'Turbo', 'Blackbody', 'Blured', 'Electric', 'Hot', 'Jet', 'Rainbow', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdBu', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'turbid', 'thermal', 'haline', 'solar', 'ice', 'gray', 'deep', 'dense', 'algae', 'matter', 'speed', 'amp', 'tempo', 'Burg', 'Burgyl', 'Redor', 'Oryel', 'Peach', 'Pinkyl', 'Mint', 'Blugrn', 'Darkmint', 'Emrld', 'Aggrnyl', 'Bluyl', 'Teal', 'Tealgrn', 'Purp', 'Purpor', 'Sunset', 'Magenta', 'Sunsetdark', 'Agsunset', 'Brwnyl']
cs_seq = [[0, "#c6ff1a"], [0.05, "#c6ff1a"], [0.05, "#ffff00"], [0.1, "#ffff00"], [0.1, "#ffcc00"], [0.15, "#ffcc00"], [0.15, "#ff944d"], [0.2, "#ff944d"], [0.2,"#ff6600"], [0.25,"#ff6600"], [0.25, "#e62e00"], [0.3, "#e62e00"], [0.3, "#cc0000"], [0.35, "#cc0000"], [0.35, "#b30059"], [0.4, "#b30059"], [0.4, "#ff0080"], [0.45, "#ff0080"], [0.45, "#ff00ff"], [0.5, "#ff00ff"], [0.5, "#bf00ff"], [0.55, "#bf00ff"], [0.55, "#8000ff"], [0.6, "#8000ff"], [0.6, "#262673"], [0.65, "#262673"], [0.65, "#4000ff"], [0.7, "#4000ff"], [0.7, "#0080ff"], [0.75, "#0080ff"], [0.75, "#00bfff"], [0.8, "#00bfff"], [0.8, "#00ffff"], [0.85, "#00ffff"], [0.85, "#00e6ac"], [0.9, "#00e6ac"], [0.9, "#009900"], [0.95, "#009900"], [0.95, "#004d00"], [0.999, "#004d00"], [1, "#cccccc"]]
cs_ternary = [[0, 'rgb(255,255,255)'], [0.33, 'rgb(255,255,255)'], [0.33, "#1DACD6"], [0.66, "#1DACD6"], [0.66, "#000066"], [0.99, "#000066"], [1, '#cccccc']]

# color hash
acids={'-': 1, 'X': 1, 'TRP': 0, 'PHE': 0.05, 'TYR': 0.1, 'ASN': 0.15, 'GLN': 0.2, 'ASP': 0.25, 'GLU': 0.3, 'SER': 0.35, 'THR': 0.4, 'HIS': 0.45, 'LYS': 0.5, 'ARG': 0.55, 'LEU': 0.6, 'ILE': 0.65, 'VAL': 0.7, 'ALA': 0.75, 'GLY': 0.8, 'MET': 0.85, 'CYS': 0.9, 'PRO': 0.95}


app = DjangoDash('ContactMap')
app.css.append_css({'external_url': '/static/css/app.css'})

app.layout = html.Div([
    dcc.Input(id="input-path", value='', type='hidden'),	# path to pdb (initial from django)
    dcc.Input(id="input-info", value='', type='hidden'),	# list of objects and residues (initial from django)
    dcc.Input(id="matrix", value='', type='hidden'),		# path to distance matrix NxN
    dcc.Input(id="residues", value='', type='hidden'),		# residues dict = {'object':['AA:ix', 'AA:ix', ...]}
    dcc.Input(id="objects", value='', type='hidden'),		# objects dict = {'id':[from, to, type-chain]}
    dcc.Input(id="contacts", value='', type='hidden'),		# contacts matrix[id1][id2] = 0 or 1 (if 2 objects in contact)
    dcc.Input(id="selected", value='', type='hidden'),		# selected object or interaction

    dcc.Tabs(id='tabs-list', value='tab-1', parent_className='custom-tabs', className='custom-tabs-container', 
        children=[
        dcc.Tab(label='OBJECTS & INTERACTIONS', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='CONTACT MAP', value='tab-2', style=tab_style, selected_style=tab_selected_style, disabled=True, disabled_style=tab_disabled_style),
    ], colors={"border": "1px solid rgba(0,0,0,1)", "background": "rgba(0,0,0,0.1)",},),
    html.Div(id='tabs', style={'height':'88vh'}),
], style={'height':'97vh', 'width':'96vw', 'margin':'0', 'padding':'0'})


@app.expanded_callback([Output('matrix', 'value'), Output('residues', 'value'), Output('objects', 'value'), Output('contacts', 'value')], [Input('input-path', 'value'), Input('input-info', 'value')])
def load_basic_data(pdb, info):

    session = pdb.split('/')
    path = os.getcwd()+'/media/'+session[0]+'/'+session[1]+'/'
    path_matrix = path+'matrix0.npy'
    matrix = np.load(path_matrix)

    objects = {}
    residues = {}
    ix_from = 0
    for num,obj in enumerate(json.loads(info)):
      code = str(obj['type']+'-'+obj['chain'])
      residues[code] = obj['residues']
      length = len(obj['residues'])
      objects[str(num)] = [ix_from, ix_from+length-1, code]
      ix_from += length

    n=len(objects)
    contacts = np.zeros(shape=(n,n), dtype = int)
    for obj1 in range(0,n):
      i = objects[str(obj1)]
      for obj2 in range(obj1,n):
        j = objects[str(obj2)]
        mat = matrix[i[0]:i[1]+1, j[0]:j[1]+1]
        mini = np.amin(mat[np.nonzero(mat)])
        if mini < 8.0:
          contacts[obj1][obj2]=1
          contacts[obj2][obj1]=1
    return [str(path_matrix), str(residues), str(objects), str(contacts)]


@app.expanded_callback(Output('cutoff','max'), Input('matrix', 'value'))
def update_max_cutoff(path_matrix):

    return round(np.amax(np.load(path_matrix)) + 1,0)


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
            html.Div(id='data', style={'height':'5vh', 'margin-top':'2vh'}),		# temporary
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
                html.Label('Select Feature', style=lab_style),
                dcc.Dropdown(id='feature_selected', placeholder="Select Feature", clearable=False, style={'margin-top':'6px'}, optionHeight = 30,
                  options=[
                    {'label': 'distance', 'value': 'D'},
                    {'label': 'hydrophobicity', 'value': 'H'},
                    {'label': 'electrostatic', 'value': 'E'},
                    {'label': 'polarity', 'value': 'P'},
                    {'label': 'aromatic', 'value': 'A'},], 
                  value='D')], style={**drop_style, 'margin-left':'1vw'} ),
              html.Div([
                html.Label('Select ColorScale', style=lab_style),
                dcc.Dropdown(id='color_selected', placeholder="Select Color", clearable=False, style={'margin-top':'6px'}, optionHeight = 30,
                  options=[{'label': i, 'value': i} for i in colors], value='ice')], style=drop_style, ),
              html.Div([
                html.Label('Reverse', style=lab_style),
                dcc.Checklist(id='reverse', options=[{'label': '', 'value': '_r'},], value='',),], 
                  style={'width': '7vw', 'marginTop':'3.5vh', 'marginLeft': '0.8vw', 'display': 'inline-block', 'vertical-align':'top'}, ),
              html.Div([
                html.Label('Select Cutoff [Å]', style=lab_style),
                dcc.Input(id="cutoff", type="number", placeholder=" default: 8Å", min=0, max=200, value='', step=0.1, debounce=True, 
                  style=dict(height='32px', width='13vw', marginTop='6px', borderRadius= '6px 6px 6px 6px', borderColor='black', color='dimgrey'))],
                style={**drop_style, 'vertical-align':'top'}, ),
              html.Div([
                html.Label('Select 1D-Y', style=lab_style),
                dcc.Dropdown(id='1dy', placeholder="Select 1D Feature", clearable=False, style={'margin-top':'6px'}, optionHeight = 30,
                  options=[
                    {'label': 'none', 'value': 'none'},
                    {'label': 'composition', 'value': 'composition'},
                    {'label': 'charged', 'value': 'charge'},
                  ], value='none')], style=drop_style, ),
              html.Div([
                html.Label('Select 1D-X', style=lab_style),
                dcc.Dropdown(id='1dx', placeholder="Select 1D Feature", clearable=False, style={'margin-top':'6px'}, optionHeight = 30,
                  options=[
                    {'label': 'none', 'value': 'none'},
                    {'label': 'composition', 'value': 'composition'},
                    {'label': 'charged', 'value': 'charge'},
                  ], value='none')], style=drop_style, ),
            ], className="content"),
            ], className="hoverable"),

            html.Div([
                dcc.Loading(id='loading-map', children=[html.Div(dcc.Graph(id='graph_map', style={'height': '94vh', 'margin-top': '0'}, 
            config={'toImageButtonOptions': {'format':'svg', 'width':1400, 'height':800, 'scale':1.5}, 'responsive': True}, ))], type='circle'),
            ], className='graph-parent'),
        ])



@app.expanded_callback([Output('data', 'children'), Output('graph_chord', 'figure')], [Input('objects', 'value'), Input('interaction_selected', 'options')])
def display_chord(obj_all, obj_con):

    objects = json.loads(obj_all.replace('\'', '\"'))

    string = ''
#    string = "The objects include: "+str(objects)

    fig = go.Figure()

    return [string, fig]


@app.expanded_callback([Output('tabs-list', 'value'), Output('selected', 'value')], [Input('object_selected', 'value'), Input('interaction_selected', 'value')])
def switch_to_map_tab(obj, interaction):
    if obj != '':
      return ['tab-2', str(obj)]
    elif interaction != '':
      return ['tab-2', str(interaction)]
    else:
      raise PreventUpdate


@app.expanded_callback(Output('graph_map', 'figure'), [Input('selected', 'value'), Input('feature_selected', 'value'), Input('color_selected', 'value'), Input('reverse', 'value'), Input('cutoff', 'value'), Input('matrix', 'value'), Input('residues', 'value'), Input('1dy', 'value')])
def display_contact_map(selected, feature, color, rv, cutoff, path_matrix, resids, y_val):

    if len(rv) > 0 and rv[0] == '_r':
      color = color+rv[0]
    desc = ''
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
    scr = len(residuesA)/len(residuesB)

    distances = np.load(path_matrix).round(decimals=3)[int(objA[1]):int(objA[2])+1, int(objB[1]):int(objB[2])+1]
    desc_d = np.copy(distances)
    desc_c = np.zeros(distances.shape, 'U3')

    if objA == objB:
      if cutoff == '':
        cutoff = 8
      maxi = np.amax(distances)
      contacts = np.copy(distances)
      contacts[contacts <= cutoff] = cutoff-1
      contacts[contacts > cutoff] = maxi
      contacts = np.tril(contacts,-1)
      m = np.nonzero(contacts)
      contacts[contacts == cutoff-1] = maxi/3
      distances[m] = contacts[m]
    elif cutoff != '':
      distances[distances > cutoff] = 0

    if cutoff == '':
      cutoff = 8
    desc_c[desc_d < cutoff] = 'YES'
    desc_c[desc_d > cutoff] = 'NO'

    dataset = []
    trace1 = go.Heatmap(x=residuesB, y=residuesA, z=distances, name='DISTANCE MAP', colorscale=color, yaxis='y1', xaxis='x1', 
        text=desc_c, hovertext=desc_d, hovertemplate='residue: %{x} in '+objB[0]+'<br>residue: %{y} in '+objA[0]+'<br>distance: %{hovertext} [Å]<br>contact cutoff: '+str(cutoff)+' [Å]<br>contact: %{text}',
        colorbar=dict(title='DISTANCES', len=0.5, x=1, y=0.25, ))

    if y_val == 'none':
      dataset = [trace1]
    else:
      residuesY = list(i.split(':')[0] for i in residuesA)
      if y_val == 'composition':
        data_seq = list(acids[i] for i in residuesY)
        trace2 = go.Bar(x=[-1]*len(residuesA), y=residuesA, orientation='h', base=0, text=residuesA, name='amino acid', hoverinfo="text+name", marker=dict(cmin=0.00, cmax=0.99, color=data_seq, colorscale=cs_seq, 
          colorbar=dict(title='SEQ', len=0.5, x=1, y=0.75, tickvals=[0.02, 0.07, 0.12, 0.17, 0.22, 0.27, 0.32, 0.37, 0.42, 0.47, 0.52, 0.57, 0.62, 0.67, 0.72, 0.77, 0.82, 0.87, 0.92, 0.97],
          ticktext=['W', 'F', 'Y', 'N', 'Q', 'D', 'E', 'S', 'T', 'H', 'K', 'R', 'L', 'I', 'V', 'A', 'G', 'M', 'C', 'P']), showscale=True), showlegend=False, yaxis='y1', xaxis='x2')
      elif y_val == 'charge':
        data_seq = list(0.75 if (i =='GLU' or i == 'ASP') else 0.35 if (i =='ARG' or i == 'LYS' or i == 'HIS') else 0.0 for i in residuesY)
        trace2 = go.Bar(x=[-1]*len(residuesA), y=residuesA, orientation='h', base=0, text=residuesA, name='charged', hoverinfo="text+name", marker=dict(cmin=0.00, cmax=0.99, color=data_seq, colorscale=cs_ternary, 
          colorbar=dict(title='CHARGE', len=0.3, x=1, y=0.75, tickvals=[0.17,0.5,0.83], ticktext=["no", "positive", "negative"]), showscale=True), showlegend=False, yaxis='y1', xaxis='x2')

      dataset = [trace1, trace2]

    return {
        'data': dataset,
        'layout': go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            autosize=True,
            hovermode='closest',
            xaxis1=dict(tickfont = dict(size = 17), title = dict(text = objB[0], font=dict(color="black", size=24)), automargin = True, scaleanchor="y", scaleratio=scr,  domain=[0, 0.87], 
                   range=[-0.6, int(objB[2])-int(objB[1])+1], tickangle = 45, showline=True),
            xaxis2=dict(tickfont = dict(size = 18), automargin = True, domain=[0.87, 0.96], tickvals=[0], ticktext=[''], showticklabels=False),
            yaxis1=dict(tickfont = dict(size = 16), title = dict(text = objA[0], font=dict(color="black", size=24)), scaleanchor="x", scaleratio=scr, domain=[0, 0.96], 
                   range=[-0.6, int(objA[2])-int(objA[1])+1], tickangle = 0, showline=True, automargin=True),
            margin=dict(t=0),
         )
    }
