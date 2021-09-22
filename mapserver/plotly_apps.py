import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import os
import plotly.graph_objects as go
from dash.dash import no_update
from dash.dependencies import Input, State, Output
from dash.exceptions import PreventUpdate
from datetime import datetime  # to be removed
from django_plotly_dash import DjangoDash

from mollib.chord import *
from mollib.patterns import calc_patterns, calc_entropy
from .models import MapModel

#    np.set_printoptions(threshold=sys.maxsize)				### testing mode
#    print('Start... ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))	### testing mode

# CSS style
drops = {'margin': '0 0 0.4vh 0.5vw', 'width': '20vw', 'display': 'inline-block', 'font-size': '2vh',
         'font-family': 'Ubuntu, sans-serif', 'color': 'dimgrey'}
lab_style = {'color': 'white', 'text-align': 'left', 'font-size': '0.85rem', 'font-weight': '500',
             'margin-left': '2px', 'font-family': 'Ubuntu, sans-serif'}
drop_style = {'margin': '1vh 0 0 2vw', 'width': '13vw', 'display': 'inline-block', 'font-size': '2vh',
              'color': 'dimgrey', 'font-family': 'Ubuntu, sans-serif'}
btn_basic = {'margin': '0 0.5vw 0 0', 'padding': '0.2vh 0', 'font-size': '2vh', 'height': '3vh', 'width': '7vw'}
btn_style = {'background-color': 'rgb(239, 239, 239)', 'color': '#4D5656', }
btn_selected_style = {'borderBottom': '3px solid #4682B4', 'borderTop': '0px solid #4682B4',
                      'background-color': '#95C8D8', 'color': 'black'}
btn_disabled_style = {'background-color': '#F8F9F9', 'color': '#95A5A6 '}
btn_opts = {'height': '4vw', 'width': '4vw', 'border': '1px', 'margin-bottom': '0.4vh', 'font-size': '3vh'}
btn_slider = {'height': '3vh', 'width': '4vw', 'display': 'inline-block', 'position': 'absolute', 'top': '0',
              'font-size': '1.7vh'}
tabs_style = {'height': '4vh', 'width': '89.5vw', 'overflow-x': 'hidden', 'overflow-y': 'hidden',
              'scrollbar-width': 'none', 'display': 'inline-block', 'margin-left': '4.5vw', 'margin-right': '0.5vw'}
settings_style = {'width': '94vw', 'height': '12vh', 'display': 'none', 'background': '#272727', 'opacity': '0.98',
                  'border-radius': '5px 5px 5px 5px', 'position': 'absolute', 'left': '4.5vw', 'z-index': '101'}

# colorscales
colors = ['Viridis', 'Cividis', 'Inferno', 'Magma', 'Plasma', 'Turbo', 'Blackbody', 'Blured', 'Electric', 'Hot', 'Jet',
          'Rainbow', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PuBu', 'PuBuGn', 'PuRd',
          'Purples', 'RdBu', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'turbid', 'thermal', 'haline',
          'solar', 'ice', 'gray', 'deep', 'dense', 'algae', 'matter', 'speed', 'amp', 'tempo', 'Burg', 'Burgyl',
          'Redor', 'Oryel', 'Peach', 'Pinkyl', 'Mint', 'Blugrn', 'Darkmint', 'Emrld', 'Aggrnyl', 'Bluyl', 'Teal',
          'Tealgrn', 'Purp', 'Purpor', 'Sunset', 'Magenta', 'Sunsetdark', 'Agsunset', 'Brwnyl']
cs_seq = [[0, "#c6ff1a"], [0.05, "#c6ff1a"], [0.05, "#ffff00"], [0.1, "#ffff00"], [0.1, "#ffcc00"], [0.15, "#ffcc00"],
          [0.15, "#ff944d"], [0.2, "#ff944d"], [0.2, "#ff6600"], [0.25, "#ff6600"], [0.25, "#e62e00"], [0.3, "#e62e00"],
          [0.3, "#cc0000"], [0.35, "#cc0000"], [0.35, "#b30059"], [0.4, "#b30059"], [0.4, "#ff0080"], [0.45, "#ff0080"],
          [0.45, "#ff00ff"], [0.5, "#ff00ff"], [0.5, "#bf00ff"], [0.55, "#bf00ff"], [0.55, "#8000ff"], [0.6, "#8000ff"],
          [0.6, "#262673"], [0.65, "#262673"], [0.65, "#4000ff"], [0.7, "#4000ff"], [0.7, "#0080ff"], [0.75, "#0080ff"],
          [0.75, "#00bfff"], [0.8, "#00bfff"], [0.8, "#00ffff"], [0.85, "#00ffff"], [0.85, "#00e6ac"], [0.9, "#00e6ac"],
          [0.9, "#009900"], [0.95, "#009900"], [0.95, "#004d00"], [0.999, "#004d00"], [1, "#cccccc"]]
cs_binary = [[0, '#ffffff'], [0.49, '#ffffff'], [0.5, '#1DACD6'], [1, '#1DACD6']]
cs_ternary = [[0, 'rgb(255,255,255)'], [0.33, 'rgb(255,255,255)'], [0.33, "#1DACD6"], [0.66, "#1DACD6"],
              [0.66, "#000066"], [0.99, "#000066"], [1, '#cccccc']]

# const. data
amino = ['W', 'F', 'Y', 'N', 'Q', 'D', 'E', 'S', 'T', 'H', 'K', 'R', 'L', 'I', 'V', 'A', 'G', 'M', 'C', 'P']

params = {'composition': [cs_seq, 'SEQUENCE', 0.45, [0.02, 0.07, 0.12, 0.17, 0.22, 0.27, 0.32, 0.37, 0.42, 0.47,
                                            0.52, 0.57, 0.62, 0.67, 0.72, 0.77, 0.82, 0.87, 0.92, 0.97], amino],
          'hydropathy': ['RdBu', 'HYDROPATHY', 0.22, [0.1, 0.5, 0.9], ['-4.5 (philic)', '0.0', '4.5 (phobic)']],
          'hydropathy_n': ['RdBu', 'HYDROPATHY<br>(normalized)', 0.22, [0.1, 0.5, 0.9],
                           ['0 (philic)', '0.5', '1 (phobic)']],
          'hydrophobic': [cs_binary, 'HYDROPHOBIC', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'amphipatic': [cs_binary, 'AMPHIPATIC', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'hydrophilic': [cs_binary, 'HYDROPHILIC', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'charged': [cs_ternary, 'CHARGE', 0.25, [0.17, 0.5, 0.83], ['NO', 'positive', 'negative']],
          'polar': [cs_binary, 'POLAR', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'nonpolar': [cs_binary, 'NONPOLAR', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'aromatic': [cs_binary, 'AROMATIC', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'π-bond': [cs_binary, 'non-aromatic<br>π-BOND', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'sulfur': [cs_ternary, 'SULFUR', 0.25, [0.17, 0.5, 0.83], ['NO', 'CYS', 'MET']],
          'H-Bond donor': [cs_binary, 'H-BOND DONOR', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'H-Bond acceptor': [cs_binary, 'H-BOND ACCEPTOR', 0.2, [0.25, 0.75], ['NO', 'YES']],
          'SEQ entropy': ['GnBu', 'ENTROPY', 0.22, [], []],
          }
opt_1D = ['none', 'composition', 'hydropathy', 'hydropathy_n', 'hydrophobic', 'amphipatic', 'hydrophilic', 'charged',
          'polar', 'nonpolar', 'aromatic', 'π-bond', 'sulfur', 'H-Bond donor', 'H-Bond acceptor', 'electrostatics',
          'SEQ entropy', 'II-structure', 'solvent access']

app = DjangoDash('ContactMap')
app.css.append_css({'external_url': '/static/css/app.css'})

app.layout = html.Div([
    dcc.Input(id="input-pk", value='', type='hidden'),  # current object pk - initial input from django
    dcc.Input(id="interval_status", value=1, type='hidden'),  # fire callback until all models have 'F' status
    dcc.Input(id="model-ix", value='', type='hidden'),  # index of selected model
    dcc.Input(id="model-data", value='', type='hidden'),  # [PDB code, matrix_path, indo]
    dcc.Input(id="con-intra", value='', type='hidden'),  # intramolecular contacts (options1)
    dcc.Input(id="con-inter", value='', type='hidden'),  # intermolecular contacts (options2)
    dcc.Input(id="contacts", value='', type='hidden'),  # list of objects + matrix of contacts counts
    dcc.Input(id="data_1d", value='', type='hidden'),  # dict of features for 1D plots
    dcc.Input(id="selected", value='', type='hidden'),  # selected object or interaction
    dcc.Input(id="data_Dist", value='', type='hidden'),  # submatrix for selected interactions
    # list = [desc_d, residuesA, residuesB, objA, objB]
    dcc.Input(id="data_Con", value='', type='hidden'),  # contacts for selected cutoff
    # list = [distances, desc_c, cutoff]
    dcc.Input(id="void1", value='', type='hidden'),
    dcc.Input(id="void2", value='', type='hidden'),
    dcc.Input(id="void3", value='', type='hidden'),
    dcc.Input(id="slider", value='', type='hidden'),

    dcc.Interval(id="interval", interval=5000),
    html.Div([
        html.Button('⯇', id="slideBack", type="button", style={'display': 'none'}),
        html.Div([html.Div(id='protein-models')], id='proteins'),
        html.Button('⯈', id="slide", type="button", style={'display': 'none'}),
    ], style={'position': 'relative'}),
    html.Div([
        html.Button('⚙', id='opts', style={**btn_basic, **btn_style, **btn_opts}, title='display settings'),
        html.Button('✾', id='tab-1', style={**btn_basic, **btn_style, **btn_opts},
                    title='see objects and interactions'),
        html.Button('◩', id='tab-2', style={**btn_basic, **btn_style, **btn_opts, 'color': '#95A5A6'},
                    title='see contact map'),
        html.Button('⬇', id='tab-3', style={**btn_basic, **btn_style, **btn_opts}, title='download data'),
    ], style={'width': '4vw', 'position': 'absolute', 'left': '0', 'z-index': '100'}),
    html.Div(id='tabs', style={'height': '94vh'}),
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
    function (n_clicks) {
      var targetDiv = document.getElementById("settings_chord");
      if (targetDiv==null) {
        var targetDiv = document.getElementById("settings_map");
      };
      if (targetDiv==null) {
        var targetDiv = document.getElementById("settings_download");
      };
      if (targetDiv.style.display !== "none") {
          targetDiv.style.display = "none";
        } else {
          targetDiv.style.display = "block";
        }
    };
    """,
    Output('void3', 'value'), [Input('opts', 'n_clicks')]
)


@app.expanded_callback(
    [Output('interval_status', 'value'), Output('protein-models', 'children'),
     Output('proteins', 'style'), Output('slide', 'style'), Output('slideBack', 'style')],
    [Input('input-pk', 'value'), Input("interval", "n_intervals"), Input('model-ix', 'value')])
def load_models(pk, n, model_ix):
    models = {}
    status = 0
    for i in list(MapModel.objects.all()):
        if i.map_id == pk:
            models[i.model_number] = i.status
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
            return [status,
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
            return [status, dcc.Dropdown(id='buttons', options=buttons, value=model_ix, placeholder='Select Model',
                                         style={'width': '20vw'}),
                    {'width': '20vw', 'vertical-align': 'middle', 'margin-left': '4.5vw'},
                    {'display': 'none'}, {'display': 'none'}]
    else:
        ix = list(models.keys())[0]
        if models[ix] == 'F':
            model_ix = ix
        else:
            status = 1
        return [status, html.Div([html.Button('M' + str(model_ix), id='buttons', value=model_ix,
                                              style={**btn_basic, **btn_selected_style, 'border': '1px solid gray'})],
                                 style={'width': '20vw'}), tabs_style, {'display': 'none'}, {'display': 'none'}]


@app.callback(Output("interval", "disabled"), [Input("interval_status", "value")])
def toggle_interval(status):
    if status == 0:
        return True
    else:
        raise PreventUpdate


@app.expanded_callback([Output('model-ix', 'value'), Output('model-data', 'value')],
                       [Input('buttons', 'value'), Input('input-pk', 'value')], [State('model-ix', 'value')])
def select_model(btn, pk, ix):
    if btn == '' or btn == ix:
        raise PreventUpdate
    elif btn == 0:
        model = MapModel.objects.get(map_id=pk)
        return [btn, [model.map.filename, model.matrix.url, model.info]]
    elif btn >= 1:
        model = MapModel.objects.get(map_id=pk, model_number=btn)
        return [btn, [model.map.filename, model.matrix.url, model.info]]


@app.expanded_callback([Output('con-intra', 'value'), Output('con-inter', 'value'), Output('contacts', 'value')],
                       [Input('model-data', 'value')])
def load_basic_data(pdb_matrix_info):
    info = json.loads(pdb_matrix_info[2])  # dict = {'protein-A':[['AA:200','AA:201', ...],[from:to]]}
    matrix = np.load(os.getcwd() + pdb_matrix_info[1])

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
                    counts = len(mat[mat <= 8.0])  # model.cutoff field needed in django
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
    return [options1, options2, [objects, contacts]]


@app.expanded_callback(Output('data_1d', 'value'), [Input('model-data', 'value')])
def calc_1d_data(pdb_matrix_info):
    info = json.loads(pdb_matrix_info[2])

    data_1d = {}
    for i in info:
        if i.startswith('protein'):
            residues = list(j.split(':')[0] for j in info[i][0])
            patterns = calc_patterns(residues)
            for z in patterns:
                data_1d[i + ':' + z] = patterns[z]
            data_1d[i + ':SEQ entropy'] = calc_entropy(residues)
    # 'electrostatics', 'II-structure', 'solvent access' - the other missing data (they will be provided by external software)
    return data_1d


@app.callback(Output('tabs', 'children'),
              [Input('tab-1', 'n_clicks'), Input('tab-2', 'n_clicks'), Input('tab-3', 'n_clicks'),
               Input('con-intra', 'value'), Input('con-inter', 'value'), Input('selected', 'value')])
def identify_objects_in_contact_and_render_content(tab1, tab2, tab3, intra, inter, selected):
    tab = 'tab-1'
    ctx = dash.callback_context.triggered
    if len(ctx):
        tmp = ctx[0]['prop_id'].split('.')[0]
        if tmp.startswith('tab'):
            tab = tmp
    if tab == 'tab-1':
        return html.Div([
            html.Div([
                html.Div([
                    html.Label('to see Intramolecular Map', style=lab_style),
                    dcc.Dropdown(id='object_selected', placeholder="Select Object", clearable=False, optionHeight=30,
                                 options=[{'label': i, 'value': intra[i]} for i in intra], value='')], style=drops, ),
                html.Div([
                    html.Label('to see Intermolecular Map', style=lab_style),
                    dcc.Dropdown(id='interaction_selected', placeholder="Select Interaction", clearable=False,
                                 optionHeight=30, options=[{'label': i, 'value': inter[i]} for i in inter], value='')],
                    style={**drops, 'margin-left': '2.5vw'}, ),
                html.Div(
                    [html.P(' or hover & click on the selected ribbon',
                            style={'color': 'gray', 'text-align': 'left', })],
                    style={'width': '40vw', 'display': 'inline-block', 'vertical-align': 'bottom'}, ),
            ], id='settings_chord', style=settings_style),

            html.Div(id='dashbio-circos', style={'height': '90vh', 'width': '94vw', 'margin': '1vh 0 0 3vw'}),
            dcc.Input(id='click-data', type='hidden'),
        ])

    elif tab == 'tab-2' and selected != '':
        return html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Label('Contact Filter', style=lab_style),
                        dcc.Dropdown(id='feature_selected', placeholder="Select Feature", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=[
                                         {'label': 'distance cutoff', 'value': 'D'},
                                         {'label': 'interaction types', 'value': 'H'},
                                         {'label': 'filter: hydrophobic', 'value': 'H'},
                                         {'label': 'filter: polar', 'value': 'P'},
                                         {'label': 'filter: charged', 'value': 'E'},
                                         {'label': 'filter: aromatic', 'value': 'A'},
                                     ], value='D')],
                        style={**drop_style, 'margin-left': '1vw', 'width': '17vw'}),
                    html.Div([
                        html.Label('ColorScale', style=lab_style),
                        dcc.Dropdown(id='color_selected', placeholder="Select Color", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=[{'label': i, 'value': i} for i in colors])],
                        style={**drop_style, 'width': '11vw'}, ),
                    html.Div([
                        html.Label('Reverse', style=lab_style),
                        dcc.Checklist(id='reverse', options=[{'label': '', 'value': '_r'}, ], value='', ), ],
                        style={'width': '6vw', 'marginTop': '3.5vh', 'marginLeft': '0.8vw', 'display': 'inline-block',
                               'vertical-align': 'top'}, ),
                    html.Div([
                        html.Label('Cutoff [Å]', style=lab_style),
                        dcc.Input(id="cutoff", type="number", placeholder=" default: 8Å", min=0, value='', step=0.1,
                                  debounce=True,
                                  style=dict(height='29px', width='10vw', marginTop='6px', color='dimgrey',
                                             borderRadius='5px 5px 5px 5px', borderColor='rgba(0,0,0,0)'))],
                        style={**drop_style, 'vertical-align': 'top', 'width': '10vw', 'margin-right': '1vw'}, ),
                    html.Div([
                        html.Label('Select 1D-Y', style=lab_style),
                        dcc.Dropdown(id='1dy', placeholder="Select 1D Feature", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=[{'label': i, 'value': i} for i in opt_1D], value='none')],
                        style={**drop_style, 'width': '17.5vw'}, ),
                    html.Div([
                        html.Label('Select 1D-X', style=lab_style),
                        dcc.Dropdown(id='1dx', placeholder="Select 1D Feature", clearable=False,
                                     style={'margin-top': '6px'}, optionHeight=30,
                                     options=[{'label': i, 'value': i} for i in opt_1D], value='none')],
                        style={**drop_style, 'width': '17.5vw'}, ),
                ]),
            ], id='settings_map', style=settings_style),

            html.Div([
                dcc.Loading(id='loading-map', type='circle',
                            children=[html.Div(dcc.Graph(id='graph_map',
                                                         style={'height': '94vh', 'width': '95vw', 'margin-top': '0',
                                                                'margin-left': '4vw'},
                                                         config={'responsive': True,
                                                             'toImageButtonOptions': {'format': 'svg', 'width': 1400,
                                                                                      'height': 800, 'scale': 1.5}}))]),
            ], className='graph-parent'),
            dcc.Input(id='click-map', type='hidden'),
            # return info of clicked point on the map;
        ])

    elif tab == 'tab-3':
        return html.Div([
            html.Div([
                html.Div([
                    html.Label('Some options_1', style=lab_style),
                    dcc.Dropdown(id='options1', placeholder="Select ...", clearable=False, optionHeight=30,
                                 options=[{'label': 'H bonds', 'value': 'HB'},
                                          {'label': 'interactions', 'value': 'I'}, ], value='')], style=drops, ),
                html.Div([
                    html.Label('Some options_2', style=lab_style),
                    dcc.Dropdown(id='options2', placeholder="Select ...", clearable=False, optionHeight=30,
                                 options=[], value='')], style={**drops, 'margin-left': '2.5vw'}, ),
            ], id='settings_download', style=settings_style),
            dcc.Textarea(id='textarea', value='Textarea content initialized\nwith multiple lines of text',
                         style={'width': '93.5vw', 'height': 300, 'margin-top': '0', 'margin-left': '4.5vw'}, ),
            html.Div(id='text-output'),
        ])
    else:
        raise PreventUpdate


@app.expanded_callback([Output('text-output', 'children')],
                       [Input('textarea', 'value'), Input('data_1d', 'value'), Input('options1', 'value')])
def load_download_section(text, dat, val):
    return ['You have entered: \n{}'.format(text)]


@app.expanded_callback(Output('dashbio-circos', 'children'), Input('contacts', 'value'))
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

    shapes = []
    ideograms = []
    ribbon_info = []

    layout = go.Layout(title='', plot_bgcolor='#FFFFFF', height=680,
                       showlegend=False, margin=dict(t=20, b=0, l=0, r=0),
                       xaxis=dict(range=[-1.4, 1.4], gridcolor='rgba(0,0,0,0)', zeroline=False, tickmode='array',
                                  tickvals=[0], ticktext=[''], ),
                       yaxis=dict(range=[-1.15, 1.15], gridcolor='rgba(0,0,0,0)', zeroline=False, tickmode='array',
                                  tickvals=[0], ticktext=[''], ),
                       )
    shapes, ideograms, ribbon_info = make_shapes_and_info(matrix, contacts, labels, ideo_colors, radii_sribb)
    layout['shapes'] = shapes
    ideograms.extend(ribbon_info)
    fig = go.Figure(data=ideograms, layout=layout)

    return dcc.Graph(id='graph-circos', figure=fig)


@app.expanded_callback(Output('click-data', 'value'), Input('graph-circos', 'clickData'))
def display_click_data(data):
    if data is not None:
        data = data["points"][0]
        if 'text' in data:
            data = data['text'].split()
            if len(data) == 5 and data[3] == 'intramolecular':
                data = data[0]
            elif len(data) == 7 and data[3] == 'intermolecular':
                data = data[0] + ':' + data[6]
        return data
    else:
        return ''


@app.expanded_callback([Output('tab-2', 'n_clicks'), Output('selected', 'value'), Output('tab-2', 'style')],
                       [Input('object_selected', 'value'), Input('interaction_selected', 'value'),
                        Input('click-data', 'value'), Input('con-intra', 'value'), Input('con-inter', 'value')],
                       [State('tab-2', 'n_clicks'), State('tab-2', 'style')])
def switch_to_map_tab(obj, interaction, click, intra, inter, n, style):
    if n is None:
        n = 0
    if obj != '':
        return [n + 1, str(obj), {**style, 'color': '#4D5656'}]
    elif interaction != '':
        return [n + 1, str(interaction), {**style, 'color': '#4D5656'}]
    elif click != '' and click is not None:
        if len(click.split(':')) == 1:
            return [n + 1, intra[click], {**style, 'color': '#4D5656'}]
        else:
            if click in inter:
                return [n + 1, inter[click], {**style, 'color': '#4D5656'}]
            else:
                click = click.split(':')
                return [n + 1, inter[click[1] + ':' + click[0]], {**style, 'color': '#4D5656'}]
    else:
        raise PreventUpdate


@app.expanded_callback(Output('color_selected', 'value'), [Input('selected', 'value')])
def switch_color(sel):
    return 'ice'


@app.expanded_callback(Output('data_Dist', 'value'), [Input('selected', 'value'), Input('model-data', 'value')])
def prepare_distance_data(selected, pdb_matrix_info):
    if selected == '':
        raise PreventUpdate
    else:
        path_matrix = os.getcwd() + pdb_matrix_info[1]
        res_list = json.loads(pdb_matrix_info[2])

        selected = selected.split('|')
        obj_a = selected[0].split(':')
        obj_b = obj_a
        if len(selected) > 1:
            obj_b = selected[1].split(':')

        residues_a = res_list[obj_a[0]][0]
        residues_b = res_list[obj_b[0]][0]

        desc_d = np.load(path_matrix)[int(obj_a[1]):int(obj_a[2]) + 1, int(obj_b[1]):int(obj_b[2]) + 1].round(
            decimals=3)

        data_dist = [desc_d, residues_a, residues_b, obj_a, obj_b]
        return data_dist


@app.expanded_callback(Output('data_Con', 'value'), [Input('cutoff', 'value'), Input('data_Dist', 'value')])
def prepare_contact_data(cutoff, data_dist):
    distances = np.array(data_dist[0])
    obj_a = data_dist[3]
    obj_b = data_dist[4]

    desc_c = np.zeros(distances.shape, 'U3')
    if cutoff == '':
        cutoff = 8.0
    desc_c[distances <= cutoff] = 'YES'
    desc_c[distances > cutoff] = 'NO'

    if obj_a == obj_b:
        maxi = np.amax(distances)
        contacts = np.copy(distances)
        contacts[contacts <= cutoff] = cutoff - 1
        contacts[contacts > cutoff] = maxi
        contacts = np.tril(contacts, -1)
        m = np.nonzero(contacts)
        contacts[contacts == cutoff - 1] = round(maxi / 3, 2)
        distances[m] = contacts[m]
    else:
        distances[distances > cutoff] = cutoff + 0.1

    data_con = [distances, desc_c, cutoff]
    return data_con


@app.expanded_callback(Output('click-map', 'value'), Input('graph_map', 'clickData'))
def display_click_map(data):
    return json.dumps(data, indent=2)


@app.expanded_callback(Output('graph_map', 'figure'),
                       [Input('feature_selected', 'value'), Input('color_selected', 'value'), Input('reverse', 'value'),
                        Input('1dy', 'value'), Input('1dx', 'value'), Input('data_1d', 'value'),
                        Input('data_Dist', 'value'), Input('data_Con', 'value'), Input('model-data', 'value')])
def display_contact_map(feature, cs, rv, y_val, x_val, data_1d, data_dist, data_con, pdb_name):
    pdb_name = pdb_name[0]
    if len(pdb_name) > 10:
        pdb_name = pdb_name[:11]
    if len(rv) > 0 and rv[0] == '_r':
        cs = cs + rv[0]
    distances = data_con[0]
    desc_c = data_con[1]
    cutoff = data_con[2]
    desc_d = data_dist[0]
    residues_a = data_dist[1]
    residues_b = data_dist[2]
    obj_a = data_dist[3]
    obj_b = data_dist[4]

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
                color = list(map(float, data_1d[obj_a[0] + ':' + y_val]))
                x_vals = [1] * len(residues_a)
                if y_val == 'SEQ entropy':
                    x_vals = color
                    cmax = np.amax(color)
                    params[y_val][3] = [0.1, cmax - 0.1]
                    params[y_val][4] = ['0.00', str(cmax)]
                if y_val == 'hydropathy':
                    x_vals = [x - 0.5 for x in color]
                    base = 0.5
            else:
                color = list(map(float, data_1d[obj_a[0] + ':hydropathy']))
                x_vals = color
            trace2 = go.Bar(x=x_vals, y=residues_a, orientation='h', base=base, text=residues_a,
                            name=y_val + '<br>' + obj_a[0], hoverlabel=dict(namelength=-1), hoverinfo="text+name",
                            marker=dict(cmin=0.00, cmax=cmax, color=color, colorscale=params[y_val][0], showscale=True,
                                        colorbar=dict(title=params[y_val][1], len=params[y_val][2], x=1, y=sc_y,
                                                      yanchor="bottom", tickvals=params[y_val][3],
                                                      ticktext=params[y_val][4]), ), showlegend=False, yaxis='y1',
                            xaxis='x2')
            dataset.append(trace2)

        if x_val != 'none':
            base = 0
            cmax = 0.99
            if x_val != 'hydropathy_n':
                color = list(map(float, data_1d[obj_b[0] + ':' + x_val]))
                y_vals = [1] * len(residues_b)
                if x_val == 'SEQ entropy':
                    y_vals = color
                    cmax = np.amax(color)
                    params[x_val][3] = [0.1, cmax - 0.1]
                    params[x_val][4] = ['0.00', str(cmax)]
                if x_val == 'hydropathy':
                    y_vals = [x - 0.5 for x in color]
                    base = 0.5
            else:
                color = list(map(float, data_1d[obj_b[0] + ':hydropathy']))
                y_vals = color
            trace3 = go.Bar(x=residues_b, y=y_vals, text=residues_b, base=base, name=x_val + '<br>' + obj_b[0],
                            hoverlabel=dict(namelength=-1), hoverinfo="text+name",
                            marker=dict(cmin=0.00, cmax=cmax, color=color, colorscale=params[x_val][0],
                                        showscale=sc_show,
                                        colorbar=dict(title=params[x_val][1], len=params[x_val][2], x=1, y=sc_x,
                                                      yanchor="top", tickvals=params[x_val][3],
                                                      ticktext=params[x_val][4]), ), showlegend=False, yaxis='y2',
                            xaxis='x1')

            dataset.append(trace3)
    trace1 = go.Heatmap(x=residues_b, y=residues_a, z=distances, name='DISTANCE MAP', colorscale=cs, yaxis='y1',
                        xaxis='x1',
                        text=desc_c, hovertext=desc_d,
                        hovertemplate='residue: %{x} in ' + obj_b[0] + '<br>residue: %{y} in ' + obj_a[
                            0] + '<br>distance: %{hovertext} [Å]<br>contact cutoff: ' + str(
                            cutoff) + ' [Å]<br>contact: %{text}',
                        colorbar=dict(title='DISTANCES', len=sc_len, x=1, y=0, yanchor="bottom"))
    dataset.append(trace1)

    return {
        'data': dataset,
        'layout': go.Layout(
            title={'text': "PDB: " + pdb_name + ", Contact Map between objects: " + obj_a[0] + " and " + obj_b[0],
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
