import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, State, Output
from dash.exceptions import PreventUpdate
from django_plotly_dash import DjangoDash


app = DjangoDash('ContactMap', suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Input(id="input-pk", value='')
])
