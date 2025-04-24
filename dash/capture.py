from io import StringIO
from dash import callback
from dash.dcc import Interval
import dash_bootstrap_components as dbc
from dash_basecomponent import BaseComponent
from dash_bootstrap_components._components import Row

def pwms_parse(text: str):
    [int(t.strip()) for t in text.split(',')]

ATTRS = ['Description', 'Motor', 'Prop']

class CaptureTab(Row, BaseComponent):

    def __init__(self, **kwargs):


        pwms_input = dbc.Row(
            [
                dbc.Label('PWMs', html_for=self.child_id('input-pwms'), width=2),
                dbc.Col(
                    dbc.Input(type='text', id=self.child_id('input-pwms'), placeholder='PWM throttle values', persistence=True),
                    width = 5
                ),
            ],
            className='mb-3',
        )


        button = dbc.Button('Start measurement', id='button-measurement', color='primary', n_clicks=0)

        attr_inputs = [self.attr_input(attr, i) for i, attr in enumerate(ATTRS)]

        form = dbc.Form([
            pwms_input,
            *attr_inputs,
            button
            ], className='m-3')

        super().__init__([
            dbc.Col([
                dbc.Card(dbc.CardBody([form]), className='m-3'),
            ]),
            dbc.Col(dbc.Card(dbc.Textarea(readOnly=True, id=self.child_id('area-log'), rows=20, value='test123\n'*10))),
            Interval(id=self.child_id('log-interval'), interval=1000, n_intervals=0, disabled=True)
        ])

    def attr_input(self, name: str, index: int):
        return dbc.Row(
            [
                dbc.Label(name, html_for=self.child_id(f'input-attr{index}'), width=2),
                dbc.Col(
                    dbc.Input(type='text', id=self.child_id(f'input-attr{index}'), placeholder=name, persistence=True),
                    width = 5
                ),
            ],
            className='mb-3',
        )

    @callback(
        BaseComponent.ChildOutput('input-pwms', 'valid'),
        BaseComponent.ChildOutput('input-pwms', 'invalid'),
        BaseComponent.ChildInput('input-pwms', 'value'),
    )
    @staticmethod
    def check_validity(text: str):
        if text:
            try:
                pwms_parse(text)
                return True, False
            except ValueError:
                pass
            return False, True

        return False, False


    strio = StringIO()

    @callback(
        BaseComponent.ChildOutput('area-log', 'value'),
        BaseComponent.ChildInput('log-interval', 'n_intervals'),
    )
    def update_log(_):
        print('a')
        # print(strio.getvalue())
        print('b')

    @callback(
        BaseComponent.ChildOutput('log-interval', 'disabled'),
        BaseComponent.ChildInput('button-measurement', 'n_clicks'),
        prevent_initial_call=True,
    )
    def on_start(_):
        print('thra')
        # print(asyncio.get_event_loop())
        # Thread(target=meas_thread, daemon=True).start()
        print('thrb')
        return False

    # def meas_thread():
    #     print('XXXX')
    #     with contextlib.redirect_stdout(strio), contextlib.redirect_stderr(strio):
    #         sleep(3)
    #     strio.write('baba')
    #     asyncio.run(testmeas())
    #     print('YYYY')

    # async def testmeas():
    #     for i in range(10):
    #         await asyncio.sleep(1)
    #         print(i)
