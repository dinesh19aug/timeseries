from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from models.forecast import Forecast
from utils.data_loader import parse_csv_contents
from utils.visuals import (
    create_metrics_table,
    plot_residuals,
    plot_combined_forecasts
)

def register_callbacks(app):
    @app.callback(
        Output('model-select', 'options'),
        Input('ensemble-option', 'value'),
        prevent_initial_call=True
    )
    def update_model_options(ensemble_opt):
        if ensemble_opt is None:
            raise PreventUpdate

        models = Forecast.get_available_models(ensemble_opt)
        return [{'label': model, 'value': model} for model in models]

    @app.callback(
        Output('ensemble-option', 'options'),
        Input('model-select', 'value'),
        prevent_initial_call=True
    )
    def update_ensemble_options(selected_models):
        if selected_models is None:
            raise PreventUpdate

        ensemble_options = Forecast.get_ensemble_options(selected_models)
        return [{'label': opt, 'value': opt} for opt in ensemble_options]
    
    @callback(
        Output('timeseries-plot', 'figure'),
        Input('upload-data', 'contents'),
        prevent_initial_call=True
    )
    def update_time_series(contents):
        if contents is None:
            raise PreventUpdate

        df = parse_csv_contents(contents)

        from plotly.graph_objs import Figure, Scatter, Layout
        fig = Figure()
        fig.add_trace(Scatter(
            x=df['date'],
            y=df['value'],
            mode='lines',
            name='Time Series Data'
        ))
        fig.update_layout(
            title="Time Series Data", 
            xaxis_title="Date", 
            yaxis_title="Value"
        )
        return fig


    @callback(
        Output('forecast-metrics', 'children'),
        Output('forecast-graphs', 'children'),
        Output('residual-plots', 'children'),
        
        Input('forecast-button', 'n_clicks'),
        
        State('model-select', 'value'),
        State('forecast-horizon', 'value'),
        State('ensemble-option', 'value'),
        State('upload-data', 'contents'),
        State('crossval-checklist', 'value'),
        State('window-type-radio', 'value'),
        prevent_initial_call=True
    )
    def run_forecast(n_clicks, models, horizon, ensemble_opt, contents, cv_checklist, window_type):
        if n_clicks is None or contents is None or not models:
            raise PreventUpdate

        # Parse the uploaded data
        df = parse_csv_contents(contents)
        
        # Set flags based on UI selections
        ensemble_flag = 'ensemble' in ensemble_opt if ensemble_opt else False
        cross_validate = 'cv_on' in cv_checklist
        
        # Display what we're doing
        print(f"\nRunning forecast with:")
        print(f"Models: {models}")
        print(f"Horizon: {horizon} days")
        print(f"Ensemble: {ensemble_flag}")
        print(f"Cross-validate: {cross_validate}")
        print(f"Window type: {window_type}")

        # Create forecast object and run the forecast
        forecast_obj = Forecast(models=models, ensemble=ensemble_flag)
        results = forecast_obj.fit_and_forecast(
            df, 
            n_days=int(horizon),
            cross_validate=cross_validate,
            window_type=window_type,
            #stride=max(1, int(horizon/3))  # Use dynamic stride based on horizon
            stride = 1
        )

        # Create the metrics table
        metrics_table = create_metrics_table(results['metrics'])

        # Create the forecast plots
        combined_plots = plot_combined_forecasts(
            results['val_truth'],
            results['val_forecasts'],
            results['forecasts']
        )

        # Create residual plots
        residual_plots = []
        
        for model_name, forecast_ts in results['val_forecasts']:
            if forecast_ts is not None and len(forecast_ts) > 0:
                residual_plot = plot_residuals(results['val_truth'], forecast_ts, model_name)
                residual_plots.append(residual_plot)

        return metrics_table, combined_plots, residual_plots