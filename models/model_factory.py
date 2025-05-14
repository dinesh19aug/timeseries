# cap_poc/models/model_factory.py

from darts.models import (
    ARIMA,
    Prophet,
    ExponentialSmoothing,
    Theta
)

AVAILABLE_MODELS = {
    "arima": ARIMA,
    "prophet": Prophet,
    "exponentialsmoothing": ExponentialSmoothing,
    "theta": Theta
}

def get_model(name: str):
    name = name.lower()
    if name not in AVAILABLE_MODELS:
        raise ValueError(f"Unsupported model: {name}")
    return AVAILABLE_MODELS[name]()