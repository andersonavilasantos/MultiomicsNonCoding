import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, title="BioMetaExplorer")

layout = html.Div(
    children=[html.H1(children="This is our upload page")]
)
