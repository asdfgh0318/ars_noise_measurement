from dataclasses import fields
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, MultiChoice, Select
from bokeh.plotting import figure
import pickle
from measurement_station import OpPointData
import math
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
import sys


def oppoint_data_src(p: OpPointData) -> dict[str, float]:
    ret = {}
    ret.update({k: v for k, v in field_entries(p.data_thrust_stand_avg).items()})
    ret.update({k: v for k, v in p.data_accustic_avg.items()})

    return ret

def field_entries(datacls) -> dict[str, float]:
    fnames = [f.name for f in fields(datacls)]
    return {n: getattr(datacls, n) for n in fnames}


def read_series(fname: str) -> dict[int, OpPointData]:
    with open(fname, 'rb') as f:
        return pickle.load(f)

def series_dataclosrc(series: dict[int, OpPointData]) -> ColumnDataSource:
    entries = [oppoint_data_src(p) for p in series.values()]
    keys = entries[0].keys()
    data = { key: [e[key] for e in entries] for key in keys }
    return ColumnDataSource(data)

def fft_datasrc(op: OpPointData) -> ColumnDataSource:
    fft_data = op.nor_report_parsed.glob_fft
    freqs = sorted(fft_data.keys())
    vals = [fft_data[f] for f in freqs]
    data = { "FREQ": freqs, "POWER": vals }
    return data


def make_doc(doc, files):
    series = [ read_series(f) for f in files ]
    sources = [series_dataclosrc(s) for s in series]
    keys = list(sources[0].data.keys())

    p = figure(title='', x_axis_label='X', y_axis_label='Y', tools=['hover', 'pan', 'xwheel_zoom'])
    p.sizing_mode = 'scale_both' # type: ignore

    multi_choice = MultiChoice(title="Y Axis", options=keys)
    xsel = Select(title="X axis:", value="", options=keys)
    srcsel = MultiChoice(title="Source:", value=files, options=files)

    colors = ['blue', 'green', 'red', 'yellow', 'orange', 'purple']

    pfft = figure(title='', x_axis_label='X', y_axis_label='Y', tools=['hover', 'pan', 'xwheel_zoom'])
    pfft.sizing_mode = 'scale_both' # type: ignore

    def update_plot(attr, _, new_values):
        p.renderers = [] # type: ignore

        p.xaxis.axis_label = xsel.value

        ymin = math.inf
        ymax = -math.inf
        
        for source, fname, color in zip(sources, files, colors):
            if fname not in srcsel.value: #type: ignore
                continue
            for column in multi_choice.value: # type: ignore
                p.line(x=xsel.value, y=column, source=source, legend_label=f'{fname} {column}', line_width=2, color=color)

                ymin = min(min(source.data[column]), ymin)
                ymax = max(max(source.data[column]), ymax)
        
        margin = (ymax-ymin) * 0.1
        p.y_range.start = ymin - margin
        p.y_range.end = ymax + margin


        pfft.renderers = [] # type: ignore
        for serie, fname, color in zip(series, files, colors):
            if fname not in srcsel.value: #type: ignore
                continue
            data = fft_datasrc(serie[1500])
            pfft.line(x='FREQ', y='POWER', source=data, legend_label=f'{fname} FFT', line_width=2, color=color)




    multi_choice.on_change('value', update_plot)
    xsel.on_change('value', update_plot)
    srcsel.on_change('value', update_plot)

    layout = column(column(srcsel, multi_choice, xsel), p, pfft)
    layout.sizing_mode = 'scale_both' # type: ignore

    doc.add_root(layout)

if __name__ == "__main__":
    files = sys.argv[1:]
    if len(files) == 0:
        print(f'Usage: {sys.argv[0]} [measurement directory/directories]')
        print(f'Examples:')
        print(f'- {sys.argv[0]} benchmark1/shroud_1m')
        print(f'- {sys.argv[0]} benchmark1/shroud_*')
        print(f'- {sys.argv[0]} benchmark1/*')
        exit()
    apps = {'/': Application(FunctionHandler(lambda doc: make_doc(doc, files)))}
    server = Server(apps, port=5000)
    print('Visualizer started. navigate to http://localhost:5000/ to continue')
    print('Exit with interrupt (Ctrl+C)')
    server.run_until_shutdown()

