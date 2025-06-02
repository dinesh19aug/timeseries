# =========================
# api/modeling.py
# =========================
from darts import TimeSeries
from darts.models import LightGBMModel, LinearRegressionModel, NaiveSeasonal, NaiveDrift
from darts.metrics import rmse
from darts.dataprocessing.transformers import Scaler
import pandas as pd

def load_series_from_csv(file_path):
    df = pd.read_csv(file_path)
    return TimeSeries.from_dataframe(df, 'Date', 'Temp')

def evaluate_models(series_list):
    results = []
    models = {
        "NaiveSeasonal": NaiveSeasonal(K=7),
        "NaiveDrift": NaiveDrift(),
        "LightGBM": LightGBMModel(lags=30),
        "LinearRegression": LinearRegressionModel(lags=30)
    }

    forecasts = {}

    for name, model in models.items():
        try:
            model.fit(series_list)
            fcasts = [model.predict(30, series=s) for s in series_list]
            backtest_rmses = [model.backtest(s, start=0.8, forecast_horizon=30, metric=rmse) for s in series_list]
            holdout_rmses = [rmse(s[-30:], f) for s, f in zip(series_list, fcasts)]
            results.append({
                "model": name,
                "backtest_rmse": sum(backtest_rmses)/len(backtest_rmses),
                "holdout_rmse": sum(holdout_rmses)/len(holdout_rmses)
            })
            forecasts[name] = [f.pd_dataframe().reset_index().rename(columns={"value": f"forecast_{name}_{i}"}) for i, f in enumerate(fcasts)]
        except Exception as e:
            results.append({"model": name, "error": str(e)})
    return {"metrics": results, "forecasts": forecasts}

def ensemble_top_models(series_list, models_to_use):
    from darts.models import RegressionEnsembleModel

    base_models = []
    for name in models_to_use:
        if name == "LightGBM":
            base_models.append(LightGBMModel(lags=30))
        elif name == "LinearRegression":
            base_models.append(LinearRegressionModel(lags=30))

    model = RegressionEnsembleModel(models=base_models, lags=30)
    model.fit(series_list)
    forecasts = [model.predict(30, series=s) for s in series_list]
    backtest_rmses = [model.backtest(s, start=0.8, forecast_horizon=30, metric=rmse) for s in series_list]
    holdout_rmses = [rmse(s[-30:], f) for s, f in zip(series_list, forecasts)]
    fcast_df = [f.pd_dataframe().reset_index().rename(columns={"value": f"forecast_Ensemble_{i}"}) for i, f in enumerate(forecasts)]
    return {
        "ensemble": [m.__class__.__name__ for m in base_models],
        "backtest_rmse": sum(backtest_rmses)/len(backtest_rmses),
        "holdout_rmse": sum(holdout_rmses)/len(holdout_rmses),
        "forecasts": fcast_df
    }

