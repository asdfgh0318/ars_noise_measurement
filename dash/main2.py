import asyncio
import contextlib
from io import StringIO
from logging import debug
from threading import Thread
from time import sleep
import dash
from dash.dash import html
from dash.dcc import Interval
import dash_bootstrap_components as dbc

from capture import CaptureTab
from db_browser import BrowseTab

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(dash.dcc.Dropdown(
                id={'dupa': 'dupa', 'index': 0},
                options=[{"label": cat, "value": cat} for cat in ['A', 'B']],
                placeholder=f"Select",
                multi=True,
                clearable=True
            ), width=6),
            dbc.Col(dash.dcc.Dropdown(
                id={'dupa': 'dupa', 'index' :1},
                options=[{"label": cat, "value": cat} for cat in ['A', 'B']],
                placeholder=f"Select",
                multi=True,
                clearable=True
            ), width=6),
            ])
    ],
    fluid=True
)

@dash.callback(
        dash.Input({'dupa': 'dupa', 'index': dash.ALL}, 'value')
)
def cb(x):
    print(x)



if __name__ == '__main__':
    app.run(host='0.0.0.0')
