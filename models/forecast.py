from darts import TimeSeries
from darts.metrics import mape, rmse
from .model_factory import AVAILABLE_MODELS, get_model
from .ensemble import ensemble_forecasts

class Forecast:
    def __init__(self, models: list, ensemble: bool = False):
        self.models = models
        self.ensemble = ensemble
        self.model_instances = {}

    def fit_and_forecast(self, df, n_days: int):
        ts = TimeSeries.from_dataframe(df, time_col='date', value_cols='value')
        # Split: 80% train, 20% validation
        split_idx = int(0.8 * len(ts))
        train, val = ts[:split_idx], ts[split_idx:]

        val_forecasts = []
        results = []
        # Validation phase
        for model_name in self.models:
            if model_name.lower() == "ensemble":
                continue  # Don't treat 'ensemble' as an actual model
            model = get_model(model_name)
            model.fit(train)
            val_forecast = model.predict(len(val))
            val_forecasts.append((model_name, val_forecast))

            metrics = {
                'model': model_name,
                'mape': mape(val, val_forecast),
                'rmse': rmse(val, val_forecast),
            }
            results.append(metrics)
            self.model_instances[model_name] = model

        # Ensemble validation
        if self.ensemble and len(val_forecasts) > 1:
            ensemble_val = ensemble_forecasts([f for _, f in val_forecasts])
            ensemble_metrics = {
                'model': 'Ensemble',
                'mape': mape(val, ensemble_val),
                'rmse': rmse(val, ensemble_val),
            }
            results.append(ensemble_metrics)
            val_forecasts.append(('Ensemble', ensemble_val))

        # Final model: fit on full data and forecast future
        forecasts = []
        full_train = ts

        for model_name in self.models:
            model = get_model(model_name)
            model.fit(full_train)
            future_forecast = model.predict(n_days)
            forecasts.append((model_name, future_forecast))

        if self.ensemble and len(forecasts) > 1:
            ensemble_forecast = ensemble_forecasts([f for _, f in forecasts])
            forecasts.append(('Ensemble', ensemble_forecast))

        return {
            'metrics': results,
            'val_forecasts': val_forecasts,
            'val_truth': val,
            'forecasts': forecasts,
            'truth': None  # future truth is unknown
        }

    
    def get_ensemble_options(models):
        if models and len(models) > 1:
            return ['ensemble']
        return []
    
    def get_available_models(include_ensemble=False):
        models = list(AVAILABLE_MODELS.keys())
        if include_ensemble and len(models) > 1:
            models.append("ensemble")
        return models