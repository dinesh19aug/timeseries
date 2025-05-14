import pandas as pd
from dash import Input, Output, State, callback_context
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import parse_contents
from models.forecast import Forecast

def register_callbacks(app):
    @app.callback(
        Output('timeseries-plot', 'figure'),
        Input('upload-data', 'contents')
    )
    def update_plot(contents):
        if contents is None:
            return {}
        df = parse_contents(contents)
        fig = px.line(df, x='date', y='value', title='Value')
        return fig

    @app.callback(
        [Output('forecast-metrics', 'children'),
         Output('forecast-graphs', 'children')],
        Input('forecast-button', 'n_clicks'),
        State('model-select', 'value'),
        State('forecast-horizon', 'value'),
        State('ensemble-option', 'value'),
        State('upload-data', 'contents')
    )
    def run_forecast(n_clicks, models, horizon, ensemble_opt, contents):
      if n_clicks is None or contents is None:
        return html.Div(), html.Div()

      df = parse_contents(contents)
      forecaster = Forecast(models=models, ensemble='ensemble' in ensemble_opt)
      results = forecaster.fit_and_forecast(df, n_days=horizon)

      # Metric Table
      metrics_table = html.Table([
          html.Tr([html.Th("Model"), html.Th("MAPE"), html.Th("RMSE")])
      ] + [
          html.Tr([html.Td(m['model']), html.Td(f"{m['mape']:.2f}"), html.Td(f"{m['rmse']:.2f}")])
          for m in results['metrics']
      ])

      # Forecast Graphs using Plotly (not Matplotlib)
      graphs = []
      for name, forecast in results['forecasts']:
          df_forecast = forecast.to_dataframe().reset_index()
          df_forecast.rename(columns={df_forecast.columns[0]: "time"}, inplace=True)

          fig = go.Figure()
          fig.add_trace(go.Scatter(
            x=df_forecast['time'],
            y=df_forecast["value"],
            mode='lines',
            name=name
        ))
          fig.update_layout(
              title=f"Forecast by {name}",
              xaxis_title='Date',
              yaxis_title='Value',
              height=400
          )
          graphs.append(dcc.Graph(figure=fig))

      return metrics_table, html.Div(graphs)