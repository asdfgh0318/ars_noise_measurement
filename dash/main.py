import asyncio
import contextlib
from io import StringIO
from logging import debug
from threading import Thread
from time import sleep
from urllib.parse import urlencode
import dash
from dash.dash import html
from dash.dcc import Interval, Store
import dash_bootstrap_components as dbc

from capture import CaptureTab
from db_browser import BrowseTab

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Tabs(
                    [
                        dbc.Tab(label="Capture", children=CaptureTab()),
                        dbc.Tab(label="Browse", children=BrowseTab()),
                        dbc.Tab(label="Analyze", id='tab_analyze', children=html.Iframe(src='http://localhost:5000/', width='100%', height=800)),
                    ]
                ),
                # width=12
            )
        ),
        Store(id='data_files', data=[])
    ],
    fluid=True
)

@dash.callback(
    dash.Output('tab_analyze', 'children'),
    dash.Input('data_files', 'data'),
)
def update_analyzer(files):
    # print('dupa')
    # print(files)
    if files:
        # return html.Iframe(src='http://localhost:5000/?'+urlencode({f'f{i}': file for i, file in enumerate(files)}), width='100%', height=800)
        return html.Iframe(src='/viz/?'+urlencode({f'f{i}': file for i, file in enumerate(files)}), width='100%', height=800)
    return dbc.Label("No measurement selected for analysis")



if __name__ == '__main__':
    app.run(host='127.0.0.1')
