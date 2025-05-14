# cap_poc/utils/visuals.py

from dash import dash_table
from dash import dcc, html
import plotly.graph_objs as go
from darts import TimeSeries

def create_metrics_table(metrics_list):
    return dash_table.DataTable(
        columns=[
            {'name': 'Model', 'id': 'model'},
            {'name': 'MAPE', 'id': 'mape'},
            {'name': 'RMSE', 'id': 'rmse'},
        ],
        data=[
            {
                'model': metric['model'],
                'mape': f"{metric['mape']:.2f}" if metric['mape'] is not None else 'N/A',
                'rmse': f"{metric['rmse']:.2f}" if metric['rmse'] is not None else 'N/A',
            }
            for metric in metrics_list
        ],
        style_table={'margin': '20px 0', 'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
    )

def plot_forecast_results(forecasts, truth=None):
    plots = []

    for model_name, forecast in forecasts:
        fig = go.Figure()

        # Only add truth if available
        if truth is not None:
            fig.add_trace(go.Scatter(
                x=truth.time_index, y=truth.values().flatten(),
                mode='lines+markers', name='Actual'
            ))

        fig.add_trace(go.Scatter(
            x=forecast.time_index, y=forecast.values().flatten(),
            mode='lines+markers', name=f'{model_name} Forecast'
        ))

        fig.update_layout(
            title=f"Forecast - {model_name}",
            xaxis_title="Date",
            yaxis_title="CPU Utilization"
        )

        plots.append(dcc.Graph(figure=fig))

    return plots

def plot_validation_forecasts(val_forecast_list: list[tuple[str, TimeSeries]], val_truth: TimeSeries):
    plots = []

    for name, forecast in val_forecast_list:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=val_truth.time_index,
            y=val_truth.values().flatten(),
            mode='lines',
            name='Actual (Validation)'
        ))

        fig.add_trace(go.Scatter(
            x=forecast.time_index,
            y=forecast.values().flatten(),
            mode='lines',
            name=f'{name} (Validation Forecast)'
        ))

        fig.update_layout(title=f"Validation Forecast vs Actual - {name}",
                          xaxis_title="Date", yaxis_title="Utilization")
        plots.append(html.Div([dcc.Graph(figure=fig)]))

    return plots