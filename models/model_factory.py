# cap_poc/models/model_factory.py

from darts.models import (
    ARIMA,
    Prophet,
    ExponentialSmoothing,
    Theta
)

def get_model(name: str):
    name = name.lower()
    if name == 'arima':
        return ARIMA()
    elif name == 'prophet':
        return Prophet()
    elif name == 'exponentialsmoothing':
        return ExponentialSmoothing()
    elif name == 'theta':
        return Theta()
    else:
        raise ValueError(f"Unsupported model: {name}")