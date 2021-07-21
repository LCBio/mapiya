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

from .models import Map, MapModel
from mollib.patterns import calc_patterns, calc_entropy
from mollib.chord import *

#    np.set_printoptions(threshold=sys.maxsize)				### testing mode
#    print('Start... ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))	### testing mode

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


# const. data
amino = ['W', 'F', 'Y', 'N', 'Q', 'D', 'E', 'S', 'T', 'H', 'K', 'R', 'L', 'I', 'V', 'A', 'G', 'M', 'C', 'P']

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
    dcc.Input(id="input-pk", value='', type='hidden'),		# current object pk - initial input from django
    dcc.Input(id="con-intra", value='', type='hidden'),		# intramolecular contacts (options1) --> to be moved to django: model.intra (field similar to info)
    dcc.Input(id="con-inter", value='', type='hidden'),		# intermolecular contacts (options2) --> to be moved to django: model.inter (field similar to info)
    dcc.Input(id="contacts", value='', type='hidden'),		# list of objects + matrix of contacts counts
    dcc.Input(id="data_1D", value='', type='hidden'),		# dict of features for 1D plots      --> to be moved to django and saved in media dir as 'patterns'
    dcc.Input(id="selected", value='', type='hidden'),		# selected object or interaction - plotly required variable
    dcc.Input(id="data_Dist", value='', type='hidden'),		# list = [desc_d, residuesA, residuesB, objA, objB] - submatrix for selected interactions - plotly required variable
    dcc.Input(id="data_Con", value='', type='hidden'),		# list = [distances, desc_c, cutoff] - contacts for selected cutoff - plotly required variable

    dcc.Tabs(id='tabs-list', value='tab-1', parent_className='custom-tabs', className='custom-tabs-container', 
        children=[
        dcc.Tab(label='OBJECTS & INTERACTIONS', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='CONTACT MAP', value='tab-2', style=tab_style, selected_style=tab_selected_style, disabled=True, disabled_style=tab_disabled_style),
        dcc.Tab(label='DOWNLOAD DATA', value='tab-3', style=tab_style, selected_style=tab_selected_style),
    ], colors={"border": "1px solid rgba(0,0,0,1)", "background": "rgba(0,0,0,0.1)",},),
    html.Div(id='tabs', style={'height':'94vh'}),
], style={'height':'97vh', 'width':'96vw', 'margin':'0', 'padding':'0'})


@app.expanded_callback([Output('con-intra', 'value'), Output('con-inter', 'value'), Output('contacts', 'value')], [Input('input-pk', 'value')])
def load_basic_data(pk):

    model = MapModel.objects.get(map_id=pk)
    info = json.loads(model.info)		# dict = {'protein-A':[['AA:200','AA:201', ...],[from:to]]}
    options1=[]
    options2=[]
    objects=[]
    contacts=np.zeros(shape=(len(info),len(info)), dtype=int)

    matrix = np.load(os.getcwd()+model.matrix.url)
    n=len(info)
    for num1, i in enumerate(info):
      objects.append(i)
      r1=info[i][1]	#range1
      for num2, j in enumerate(info):
        if num2 >= num1:
          r2=info[j][1]	#range2
          mat = matrix[r1[0]:r1[1], r2[0]:r2[1]]
          mat = mat[np.nonzero(mat)]
          counts = 0
          try:
            counts = len(mat[mat <= 8.0])	# model.cutoff field needed in django (filled out by user via input option on the initial mapserver view)
            if counts > 0:
              if num1==num2:
                val = i+":"+str(r1[0])+":"+str(r1[1])+":"+str(counts)
                options1.append({'label': i, 'value': val})
              else:
                val = i+":"+str(r1[0])+":"+str(r1[1])+"|"+j+":"+str(r2[0])+":"+str(r2[1])+"|"+str(counts)
                options2.append({'label': i+":"+j, 'value': val})
          except ValueError:
            pass
          contacts[num1][num2] = counts
          contacts[num2][num1] = counts
    return [options1, options2, [objects,contacts]]


@app.expanded_callback(Output('data_1D', 'value'), Input('input-pk', 'value'))
def calc_1D_data(pk):
    
    model = MapModel.objects.get(map_id=pk)
    info = json.loads(model.info)

    data_1D = {}
    for i in info:
      if i.startswith('protein'):
        residues = list(i.split(':')[0] for i in info[i][0])
        patterns = calc_patterns(residues)
        for z in patterns:
          data_1D[i+':'+z] = patterns[z]
        data_1D[i+':SEQ entropy'] = calc_entropy(residues)
# 'electrostatics', 'II-structure', 'solvent access' - the other missing data (they will be provided by external software)
    return data_1D


@app.callback(Output('tabs', 'children'), [Input('tabs-list', 'value'), Input('con-intra', 'value'), Input('con-inter', 'value')])
def identify_objects_in_contact_and_render_content(tab, intra, inter):

    if tab == 'tab-1':
        return html.Div([
            html.Div([
              html.Div([
                html.Label('to see Intermolecular Map', style=labs),
                dcc.Dropdown(id='object_selected', placeholder="Select Object", clearable=False, optionHeight = 30,
                  options=intra, value='')], style=drops,),
              html.Div([
                html.Label('to see Intramolecular Map', style=labs),
                dcc.Dropdown(id='interaction_selected', placeholder="Select Interaction", clearable=False, optionHeight = 30,
                  options=inter, value='')], style={**drops, 'margin-left': '2.5vw'},),
            ]),
            html.Div(id='dashbio-circos', style={'width':'90vw', 'marginLeft':'0vw'}),
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


@app.expanded_callback(Output('dashbio-circos', 'children'), Input('contacts', 'value'))
def display_circos(data):

    labels = data[0]
    contacts = data[1]
    matrix=normalize_contact_counts(contacts)
    radii_sribb=[0.3]*len(labels)
    ideo_colors=['rgba(186,225,255,0.9)', 'rgba(186,255,201,0.9)', 'rgba(255,255,186,0.9)', 'rgba(255,223,186,0.9)', 'rgba(224,194,143,0.9)', 'rgba(255,154,130,0.9)', 'rgba(255,179,186,0.9)', 'rgba(209, 135, 135,0.9)', 'rgba(184,161,177,0.9)', 'rgba(211,195,181,0.9)', ]  #pink, orange, yellow, green, blue, purple, brown, gray

    k=len(labels)/len(ideo_colors)
    if k>1:
      new_colors=[]
      for i in range(int(k)+1):
        new_colors.extend(ideo_colors)
      ideo_colors = new_colors

    shapes = []
    ideograms = []
    ribbon_info = []

    layout = go.Layout(title='', 
      plot_bgcolor='#FFFFFF', height=680, showlegend=False, margin=dict(t=20,b=0,l=0, r=0),
      xaxis=dict(range=[-1.4,1.4], gridcolor='rgba(0,0,0,0)', zeroline=False, tickmode='array', tickvals=[0], ticktext=[''],),
      yaxis=dict(range=[-1.15,1.15], gridcolor='rgba(0,0,0,0)', zeroline=False, tickmode='array', tickvals=[0], ticktext=[''],),
    )
    shapes, ideograms, ribbon_info = make_shapes_and_info(matrix, contacts, labels, ideo_colors, radii_sribb)
    layout['shapes'] = shapes

    data = go.Data(ideograms+ribbon_info)
    fig = go.Figure(data=data, layout=layout)

    return dcc.Graph(figure=fig)


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
      return 'ice'


@app.expanded_callback(Output('data_Dist', 'value'), [Input('selected', 'value'), Input('input-pk', 'value')])
def prepare_distance_data(selected, pk):

    if selected == '':
      raise PreventUpdate
    else:
      model = MapModel.objects.get(map_id=pk)
      path_matrix=os.getcwd()+model.matrix.url
      res_list = json.loads(model.info)

      selected = selected.split('|')
      objA = selected[0].split(':')
      objB = objA
      if len(selected) > 1:
        objB = selected[1].split(':')

      residuesA = res_list[objA[0]][0]
      residuesB = res_list[objB[0]][0]

      desc_d = np.load(path_matrix)[int(objA[1]):int(objA[2])+1, int(objB[1]):int(objB[2])+1].round(decimals=3)

      dataDist = [desc_d, residuesA, residuesB, objA, objB]
      return dataDist


@app.expanded_callback(Output('data_Con', 'value'), [Input('cutoff', 'value'), Input('data_Dist', 'value')])
def prepare_contact_data(cutoff, dataDist):

    distances = np.array(dataDist[0])
    objA = dataDist[3]
    objB = dataDist[4]

    desc_c = np.zeros(distances.shape, 'U3')
    if cutoff == '':
      cutoff = 8.0
    desc_c[distances <= cutoff] = 'YES'
    desc_c[distances > cutoff] = 'NO'

    if objA == objB:
      maxi = np.amax(distances)
      contacts = np.copy(distances)
      contacts[contacts <= cutoff] = cutoff-1
      contacts[contacts > cutoff] = maxi
      contacts = np.tril(contacts,-1)
      m = np.nonzero(contacts)
      contacts[contacts == cutoff-1] = round(maxi/3,2)
      distances[m] = contacts[m]
    else:
      distances[distances > cutoff] = cutoff+0.1

    dataCon = [distances, desc_c, cutoff]
    return dataCon


@app.expanded_callback(Output('graph_map', 'figure'), [Input('feature_selected', 'value'), Input('color_selected', 'value'), Input('reverse', 'value'), Input('1dy', 'value'), Input('1dx', 'value'), Input('data_1D', 'value'), Input('data_Dist', 'value'), Input('data_Con', 'value')])
def display_contact_map(feature, cs, rv, y_val, x_val, data1D, dataDist, dataCon):



    if len(rv) > 0 and rv[0] == '_r':
      cs = cs+rv[0]

    distances = dataCon[0]
    desc_c = dataCon[1]
    cutoff = dataCon[2]
    desc_d = dataDist[0]
    residuesA = dataDist[1]
    residuesB = dataDist[2]
    objA = dataDist[3]
    objB = dataDist[4]

    dataset = []
    ax = 0.96
    if x_val != 'none':
      ax = 0.88

    sc_len = 0.975
    if y_val != 'none' or x_val != 'none':
      sc_len = 0.5

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
            xaxis1=dict(tickfont = dict(size = 17), title = dict(text = objB[0], font=dict(color="black", size=24)), automargin = True, domain=[0, 0.87], range=[-1, int(objB[2])-int(objB[1])+1], tickangle = 45, showline=True),
            xaxis2=dict(tickfont = dict(size = 18, color="gray"), automargin = True, domain=[0.87, 0.955],tickmode='array', tickvals=[0.5], ticktext=[y_val+'-'+objA[0].split('-')[1]],  tickangle = 45),
            yaxis1=dict(tickfont = dict(size = 16), title = dict(text = objA[0], font=dict(color="black", size=24)), domain=[0, ax], range=[-0.9, int(objA[2])-int(objA[1])+1], tickangle = 0, showline=True, automargin=True),
            yaxis2=dict(tickfont = dict(size = 16, color="gray"), tickmode='array', tickvals=[0.5], ticktext=[x_val+'-'+objB[0].split('-')[1]], domain=[0.88, 0.965], showline=False, automargin = True),
            margin=dict(t=0),
         )
    }
