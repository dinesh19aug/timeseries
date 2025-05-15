from darts import TimeSeries
from darts.metrics import mape, rmse
from .model_factory import AVAILABLE_MODELS, get_model
from .ensemble import ensemble_forecasts
from darts.utils.utils import ModelMode




class Forecast:
    def __init__(self, models: list, ensemble: bool = False):
        self.models = models
        self.ensemble = ensemble
        self.model_instances = {}


    
    def get_ensemble_options(models):
        if models and len(models) > 1:
            return ['ensemble']
        return []
    
    def get_available_models(include_ensemble=False):
        models = list(AVAILABLE_MODELS.keys())
        if include_ensemble and len(models) > 1:
            models.append("ensemble")
        return models
    

    

    def fit_and_forecast(
        self,
        df,
        n_days: int,
        cross_validate: bool = False,
        window_type: str = 'expanding',  # or 'sliding'
        stride: int = 1):
        
        ts = TimeSeries.from_dataframe(df, time_col='date', value_cols='value')
        # Split: 80% train, 20% validation
        split_idx = int(0.8 * len(ts))
        train, val = ts[:split_idx], ts[split_idx:]

        val_forecasts = []
        results = []

        # Validation phase
        for model_name in self.models:
            if model_name.lower() == "ensemble":
                continue  # Skip 'ensemble' as standalone model
            model = get_model(model_name)

            if cross_validate:
                # Generate backtest forecasts with more verbose output
                print(f"Running historical forecasts for {model_name}...")
               # Target: 30 windows
                target_windows = 30
                stride = max(1, (len(ts) - n_days) // (target_windows - 1))
                

                start = len(ts) - n_days - stride * (target_windows - 1)
                start = max(0, start)

                print(f"Start index: {start}, Expected windows: {(len(ts) - start - n_days) // stride + 1}")
                backtest_forecast = model.historical_forecasts(
                    ts,
                    start=start,  # Start from 80% of the data
                    forecast_horizon=n_days,
                    stride= stride,
                    retrain=True,
                    verbose=True,
                    overlap_end=True,
                    
                )
                
                print(f"Generated {len(backtest_forecast)} backtest forecasts for {model_name}")
               
                # Find the forecast that most closely aligns with the validation period
                # For visualization, get the forecast that starts closest to val.start_time()
                best_forecast = None
                min_diff = float('inf')
                
                for f in backtest_forecast:
                    if f is not None and len(f) > 0:
                        time_diff = abs((f.start_time() - val.start_time()).total_seconds())
                        if time_diff < min_diff:
                            min_diff = time_diff
                            best_forecast = f
                
                # Calculate metrics with all backtest forecasts
                # Align actuals with forecasted series
                actuals = []
                valid_forecasts = []
                
                for f in backtest_forecast:
                    if f is not None and len(f) > 0:
                        actual_slice = ts.slice(f.start_time(), f.end_time())
                        if len(actual_slice) > 0:
                            actuals.append(actual_slice)
                            print("Appending valid_forecasts ", f.start_time(), f.end_time())
                            valid_forecasts.append(f)

                if actuals and valid_forecasts:
                    score = {
                        'model': f"{model_name} (CV)",
                        'mape': mape(actuals, valid_forecasts),
                        'rmse': rmse(actuals, valid_forecasts),
                    }
                    
                    # Store the best forecast for visualization
                    if valid_forecasts is not None:
                        #print(f"Adding CV forecast for {model_name}: {valid_forecasts.start_time()} to {valid_forecasts.end_time()}")
                        val_forecasts.append((f"{model_name} (CV)", valid_forecasts))
                    
                    
                    results.append(score)
                else:
                    results.append({
                        'model': f"{model_name} (CV)",
                        'mape': None,
                        'rmse': None,
                    })

            else:
                # Fit on training and validate
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

        # Ensemble on validation
        if self.ensemble and len(val_forecasts) > 1:
            val_series = [f for _, f in val_forecasts if isinstance(f, TimeSeries)]
            ensemble_val = ensemble_forecasts(val_series)
            ensemble_metrics = {
                'model': 'Ensemble',
                'mape': mape(val, ensemble_val),
                'rmse': rmse(val, ensemble_val),
            }
            results.append(ensemble_metrics)
            val_forecasts.append(('Ensemble', ensemble_val))

        # Forecast future
        forecasts = []
        full_train = ts

        for model_name in self.models:
            if model_name.lower() == "ensemble":
                continue
            model = get_model(model_name)
            model.fit(full_train)
            future_forecast = model.predict(n_days)
            forecasts.append((model_name, future_forecast))

        if self.ensemble and len(forecasts) > 1:
            future_series = [f for _, f in forecasts]
            ensemble_forecast = ensemble_forecasts(future_series)
            forecasts.append(('Ensemble', ensemble_forecast))
        
        # Debug output
        print("\nValidation forecasts:")
        for name, f in val_forecasts:
            print(f"→ {name}: {type(f)} | len: {len(f) if isinstance(f, TimeSeries) else 'N/A'}")
            if isinstance(f, TimeSeries):
                print(f"  Time range: {f.start_time()} - {f.end_time()}")
        
        print("\nFuture forecasts:")
        for name, f in forecasts:
            print(f"→ {name}: {type(f)} | len: {len(f)}")
            print(f"  Time range: {f.start_time()} - {f.end_time()}")
        
        return {
            'metrics': results,
            'val_forecasts': val_forecasts,
            'val_truth': val,
            'forecasts': forecasts,
            'truth': ts  # Pass the full time series for better plots
        }