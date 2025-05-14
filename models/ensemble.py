# cap_poc/models/ensemble.py

from darts import TimeSeries

def ensemble_forecasts(forecasts: list[TimeSeries]) -> TimeSeries:
    if not forecasts:
        raise ValueError("No forecasts to ensemble.")
    return sum(forecasts) / len(forecasts)