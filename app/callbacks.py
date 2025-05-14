from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from models.forecast import Forecast
from utils.data_loader import parse_csv_contents
from utils.visuals import (
    plot_forecast_results,
    plot_validation_forecasts,
    create_metrics_table
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
            name='Passengers'
        ))
        fig.update_layout(title="CPU Utilization Time Series", xaxis_title="Date", yaxis_title="Utilization")
        return fig


    @callback(
        Output('forecast-metrics', 'children'),
        Output('forecast-graphs', 'children'),
        Input('forecast-button', 'n_clicks'),
        State('model-select', 'value'),
        State('forecast-horizon', 'value'),
        State('ensemble-option', 'value'),
        State('upload-data', 'contents'),
        prevent_initial_call=True
    )
    def run_forecast(n_clicks, models, horizon, ensemble_opt, contents):
        if n_clicks is None or contents is None or not models:
            raise PreventUpdate

        df = parse_csv_contents(contents)
        ensemble_flag = 'ensemble' in ensemble_opt if ensemble_opt else False

        forecast_obj = Forecast(models=models, ensemble=ensemble_flag)
        results = forecast_obj.fit_and_forecast(df, n_days=int(horizon))

        metrics_table = create_metrics_table(results['metrics'])

        # Validation forecast plots
        val_plots = plot_validation_forecasts(results['val_forecasts'], results['val_truth'])

        # Future forecast plots
        forecast_plots = plot_forecast_results(results['forecasts'], results['truth'])

        return metrics_table, val_plots + forecast_plots