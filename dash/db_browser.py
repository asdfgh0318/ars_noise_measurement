import asyncio
import contextlib
from io import StringIO
from logging import debug
from threading import Thread
from time import sleep
import dash
from dash.dash import dcc, html
from dash_basecomponent import BaseComponent
import dash_bootstrap_components as dbc
import pandas as pd

data = pd.DataFrame([
    {'Prop': 'N/A', 'Motor': 'N/A', 'Description': 'baseline_chamber', 'Shroud': 'None', 'id': 'data_misc/benchmark_tent/baseline_chamber'},
    {'Prop': 'N/A', 'Motor': 'N/A', 'Description': 'baseline_notent', 'Shroud': 'None', 'id': 'data_misc/benchmark_tent/baseline_notent'},
    {'Prop': 'N/A', 'Motor': 'N/A', 'Description': 'baseline_tent', 'Shroud': 'None', 'id': 'data_misc/benchmark_tent/baseline_tent'},
    {'Prop': 'N/A', 'Motor': 'N/A', 'Description': 'shroud_chamber', 'Shroud': 'Yes', 'id': 'data_misc/benchmark_tent/shroud_chamber'},
    {'Prop': 'N/A', 'Motor': 'N/A', 'Description': 'shroud_nochamber', 'Shroud': 'Yes', 'id': 'data_misc/benchmark_tent/shroud_nochamber'},
    {'Prop': 'N/A', 'Motor': 'N/A', 'Description': 'shroud_foam_chamber', 'Shroud': 'With foam', 'id': 'data_misc/benchmark_tent/shroud_foam_chamber'},
])

ATTRS = ['Description', 'Motor', 'Prop', 'Shroud']
# ATTRS = ['Description']

def is_checked(value) -> bool:
    if not isinstance(value, list):
        return False
    return None in value


class BrowseTab(dbc.Container, BaseComponent):


    def __init__(self, **kwargs):

        attr_filters = [self.attr_filter(attr, i) for i, attr in enumerate(ATTRS)]

        super().__init__([
            html.H2("Database browser"),
            *attr_filters,

            dbc.Row([
                dbc.Col(dbc.Table(id=self.child_id("data-table"), bordered=True, hover=True, responsive=True, striped=True), width=8)
            ])
        ])

        @dash.callback(
            dash.Output(self.child_id('data-table'), 'children'),
            dash.Input({'role': 'filter-attr', 'index': dash.ALL}, "value"),
        )
        def update_table(filters):
            filtered_data = data.copy()

            for attr, filt in zip(ATTRS, filters):
                if filt:
                    filtered_data = filtered_data[filtered_data[attr].isin(filt)] # type: ignore

            def attr_col(attr: str):
                vals = [html.Td(x) for x in filtered_data[attr]]
                return html.Th(attr), vals


            cols_attrs = [attr_col(attr) for attr in ATTRS] # type: ignore
            col_sel = html.Th('Compare'), [html.Td(dcc.Checklist(options=[{'label': ''}], value=True, inline=True, id={'role': 'row-compare', 'id': row["id"]}, )) for _, row in filtered_data.iterrows()] # type: ignore

            cols = cols_attrs + [col_sel]

            header = html.Thead(html.Tr([h for h, b in cols]))

            bodyrows = zip(*[b for h, b in cols])

            body = html.Tbody([html.Tr([data for data in row]) for row in bodyrows])



            return [header, body]

        @dash.callback(
            # dash.Output(self.child_id('data-table'), 'children'),
            dash.Output('data_files', 'data'),
            dash.Input({'role': 'row-compare', 'id': dash.ALL}, "value"),
            dash.State({'role': 'row-compare', 'id': dash.ALL}, "id"),
        )
        def duppa(values, ids):
            print('kkkk')
            values = list(map(is_checked, values))
            # values = list(map(bool, values))
            ids = list(map(lambda x: x['id'], ids))
            # print(values)
            # print(ids)
            return [idd for idd, val, in zip(ids, values) if val]

    def attr_filter(self, name: str, index: int):
        r = dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id={'role':'filter-attr', 'index': index},
                    options=[{"label": cat, "value": cat} for cat in sorted(data[name].unique())],
                    placeholder=f"Select {name}",
                    multi=True,
                    clearable=True
                ), width=6)
            ], className="mb-3")
        return r
