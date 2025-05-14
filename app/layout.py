from dash import html, dcc

layout = html.Div([
    html.H2("CPU Utilization Forecasting Tool"),

    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload CSV'),
        multiple=False
    ),

    dcc.Graph(id='timeseries-plot'),

    html.Div([
        html.Label('Select Models:'),
        dcc.Checklist(
            id='model-select',
            options=[
                {'label': 'ARIMA', 'value': 'ARIMA'},
                {'label': 'Prophet', 'value': 'Prophet'},
                {'label': 'ExponentialSmoothing', 'value': 'ExponentialSmoothing'},
                {'label': 'Theta', 'value': 'Theta'}
            ]
        ),

        html.Label('Forecast Horizon (days):'),
        dcc.Input(id='forecast-horizon', type='number', min=1, value=30),

        dcc.Checklist(
            id='ensemble-option',
            options=[{'label': 'Use Ensemble', 'value': 'ensemble'}],
            value=[]
        ),

        html.Button('Forecast', id='forecast-button')
    ]),

    html.Hr(),
    html.Div(id='forecast-metrics'),
    html.Div(id='forecast-graphs')
])