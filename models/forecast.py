from darts import TimeSeries
from darts.metrics import mape, rmse
from .model_factory import get_model
from .ensemble import ensemble_forecasts

class Forecast:
    def __init__(self, models: list, ensemble: bool = False):
        self.models = models
        self.ensemble = ensemble
        self.model_instances = {}

    def fit_and_forecast(self, df, n_days: int):
        ts = TimeSeries.from_dataframe(df, time_col='date', value_cols='value')
        train, val = ts[:-n_days], ts[-n_days:]

        results = []
        forecasts = []

        for model_name in self.models:
            model = get_model(model_name)
            model.fit(train)
            forecast = model.predict(n_days)
            forecasts.append((model_name, forecast))

            metrics = {
                'model': model_name,
                'mape': mape(val, forecast),
                'rmse': rmse(val, forecast),
            }
            results.append(metrics)
            self.model_instances[model_name] = model

        if self.ensemble and len(forecasts) > 1:
            ensemble_forecast = ensemble_forecasts([f for _, f in forecasts])
            ensemble_metrics = {
                'model': 'Ensemble',
                'mape': mape(val, ensemble_forecast),
                'rmse': rmse(val, ensemble_forecast),
            }
            results.append(ensemble_metrics)
            forecasts.append(('Ensemble', ensemble_forecast))

        return {
            'metrics': results,
            'forecasts': forecasts,
            'truth': val
        }