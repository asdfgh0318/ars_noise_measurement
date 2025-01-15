from dataclasses import fields
from typing import Iterable, Sequence
from bokeh.core.enums import SizingMode, SizingModeType
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, MultiChoice, Select
from bokeh.plotting import figure
import pickle

from measurement_station import OpPointData


def oppoint_data_src(p: OpPointData) -> dict[str, float]:
    ret = {}

    # print(fields(p.data_thrust_stand_avg)[0])

    ret.update({k: v for k, v in field_entries(p.data_thrust_stand_avg).items()})

    return ret

def field_entries(datacls) -> dict[str, float]:
    fnames = [f.name for f in fields(datacls)]
    return {n: getattr(datacls, n) for n in fnames}


def read_series(fname: str) -> dict[int, OpPointData]:
    with open(fname, 'rb') as f:
        return pickle.load(f)

def series_dataclosrc(series: dict[int, OpPointData]) -> ColumnDataSource:
    # entries = [field_entries(v) for v in series.values()]
    entries = [oppoint_data_src(p) for p in series.values()]
    keys = entries[0].keys()
    data = { key: [e[key] for e in entries] for key in keys }
    return ColumnDataSource(data)


filespeed = 15

files = [ f'./dmuch/gf7035_v{filespeed}.pickle', f'./dmuch/gf7042_v{filespeed}.pickle', f'./dmuch/apc838_v{filespeed}.pickle', f'./dmuch/apc938_v{filespeed}.pickle', f'./dmuch/ep_v{filespeed}.pickle' ]

series = [ read_series(f) for f in files ]

print(oppoint_data_src(series[0][1500]))

print(series_dataclosrc(series[0]))

sources = [series_dataclosrc(s) for s in series]

keys = list(sources[0].data.keys())






p = figure(title="Dynamic Column Plot", x_axis_label='Index', y_axis_label='Value', tools=['hover', 'pan', 'xwheel_zoom'])
p.sizing_mode = 'scale_both' # type: ignore

multi_choice = MultiChoice(title="Choose Columns to Plot", options=keys)
xsel = Select(title="Y axis:", value="cos", options=keys)

colors = ['blue', 'green', 'red', 'yellow', 'orange']

def update_plot(attr, _, new_values):
    p.renderers = [] # type: ignore
    
    for source, fname, color in zip(sources, files, colors):
        for column in multi_choice.value: # type: ignore
            p.line(x=xsel.value, y=column, source=source, legend_label=f'{fname} {column}', line_width=2, color=color)

multi_choice.on_change('value', update_plot)
xsel.on_change('value', update_plot)

layout = column(multi_choice, xsel, p)
layout.sizing_mode = 'scale_both' # type: ignore

curdoc().add_root(layout)
