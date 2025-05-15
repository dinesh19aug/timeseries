from dash import html, dcc

layout = html.Div([
    html.H2("Time Series Forecasting Tool", style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    # File Upload section
    html.Div([
        html.H4("Step 1: Upload Data"),
        dcc.Upload(
            id='upload-data',
            children=html.Button('Upload CSV', style={'width': '100%'}),
            multiple=False,
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px 0'
            }
        ),
    ], style={'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'marginBottom': '20px'}),

    # Time series plot
    html.Div([
        html.H4("Data Preview"),
        dcc.Graph(id='timeseries-plot')
    ], style={'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'marginBottom': '20px'}),

    # Forecast configuration
    html.Div([
        html.H4("Step 2: Configure Forecast"),
        
        # Model selection
        html.Div([
            html.Label('Select Models:', style={'fontWeight': 'bold'}),
            dcc.Checklist(
                id='model-select',
                options=[
                    {'label': ' ARIMA', 'value': 'ARIMA'},
                    {'label': ' Prophet', 'value': 'Prophet'},
                    {'label': ' Exponential Smoothing', 'value': 'ExponentialSmoothing'},
                    {'label': ' Theta', 'value': 'Theta'}
                ],
                style={'marginBottom': '15px'}
            ),
        ], style={'marginBottom': '15px'}),
        
        # Ensemble option
        html.Div([
            dcc.Checklist(
                id='ensemble-option',
                options=[{'label': ' Use Ensemble', 'value': 'ensemble'}],
                value=[],
                style={'marginBottom': '15px'}
            ),
        ]),
        
        # Forecast horizon
        html.Div([
            html.Label('Forecast Horizon (days):', style={'fontWeight': 'bold'}),
            dcc.Input(
                id='forecast-horizon', 
                type='number', 
                min=1, 
                value=30,
                style={'width': '100px', 'marginLeft': '10px'}
            ),
        ], style={'marginBottom': '15px'}),
        
        # Cross-validation settings
        html.Div([
            html.H5("Cross-Validation Settings:"),
            
            # Enable cross-validation
            html.Div([
                dcc.Checklist(
                    id='crossval-checklist',
                    options=[{'label': ' Enable Cross-Validation', 'value': 'cv_on'}],
                    value=[]
                ),
            ], style={'marginBottom': '10px'}),
            
            # Window type
            html.Div([
                html.Label("Window Type:", style={'marginRight': '10px'}),
                dcc.RadioItems(
                    id='window-type-radio',
                    options=[
                        {'label': ' Expanding', 'value': 'expanding'},
                        {'label': ' Sliding', 'value': 'sliding'}
                    ],
                    value='expanding',
                    labelStyle={'display': 'inline-block', 'marginRight': '15px'}
                ),
            ]),
        ], style={'marginBottom': '15px', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
        
        # Run button
        html.Button(
            'Run Forecast', 
            id='forecast-button',
            style={
                'backgroundColor': '#007bff',
                'color': 'white',
                'padding': '10px 20px',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'marginTop': '10px'
            }
        )
    ], style={'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'marginBottom': '20px'}),

    html.Hr(),
    
    # Results section
    html.Div([
        html.H4("Step 3: Results"),
        
        # Metrics table
        html.Div([
            html.H5("Forecast Metrics:"),
            html.Div(id='forecast-metrics')
        ], style={'marginBottom': '20px'}),
        
        # Forecast graphs
        html.Div([
            html.H5("Forecast Plots:"),
            html.Div(id='forecast-graphs')
        ], style={'marginBottom': '20px'}),
        
        # Residual plots
        html.Div([
            html.H5("Residual Analysis:"),
            html.Div(id='residual-plots')
        ])
    ], style={'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'})
], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})