# cap_poc/utils/visuals.py

from dash import dash_table
from dash import dcc, html
import plotly.graph_objs as go
from darts import TimeSeries
import numpy as np
from darts import concatenate


def format_metric(metric_value):
    if metric_value is None:
        return 'N/A'
    elif isinstance(metric_value, list) or isinstance(metric_value, tuple):
        values = [v for v in metric_value if v is not None]
        if not values:
            return 'N/A'
        return f"{np.mean(values):.2f} ± {np.std(values):.2f}"
    else:
        return f"{metric_value:.2f}"

def create_metrics_table(metrics: list[dict]):
    data = []
    for metric in metrics:
        data.append({
            'Model': metric['model'],
            'MAPE': format_metric(metric['mape']),
            'RMSE': format_metric(metric['rmse']),
        })

    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in ['Model', 'MAPE', 'RMSE']],
        data=data,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
    )

def plot_combined_forecasts(val_truth, val_forecasts, future_forecasts):
    """
    Create combined plots showing the validation and future forecasts for each model.
    
    Args:
        val_truth: The validation part of the time series (actual values)
        val_forecasts: List of tuples (model_name, forecast) for validation
        future_forecasts: List of tuples (model_name, forecast) for future predictions
        
    Returns:
        List of dash graph components
    """
    figures = []
    
    # Create lookup for future forecasts
    future_dict = {clean_model_name(name): forecast for name, forecast in future_forecasts}
    
    # Process each model's forecasts
    for model_name, val_forecast in val_forecasts:
        print(f"\nCreating combined plot for {model_name}")
        
        # Skip if the forecast is None or empty
        if val_forecast is None or len(val_forecast) == 0:
            print(f"⚠️ Skipping plot for {model_name}: empty forecast")
            continue
            
        print(f"Type of val_forecast: {type(val_forecast)}")
        
        # Create figure for this model
        fig = go.Figure()
        # Align val_truth to the same period as the validation forecast
        
        # Plot the actuals (validation truth)
        fig.add_trace(go.Scatter(
            x=val_truth.time_index, 
            y=val_truth.values().flatten(),
            mode='lines',
            name='Actuals',
            line=dict(color='black')
        ))
        
        # Plot the validation forecast(s)
        if isinstance(val_forecast, list):
            # Filter out empty forecasts
            valid_slices = [f for f in val_forecast if f is not None and len(f) > 0]
            if not valid_slices:
                print(f"⚠️ No valid CV slices for {model_name}")
                continue
            try:
                # Merge all CV forecasts into one TimeSeries
                merged_forecast = concatenate(valid_slices, ignore_time_axis=False)
                fig.add_trace(go.Scatter(
                        x=merged_forecast.time_index,
                        y=merged_forecast.values().flatten(),
                        mode='lines',
                        name=f'{model_name} CV',
                        line=dict(color='orange', dash='dot'),
                        opacity=0.6
                    ))
            except Exception as e:
                print(f"⚠️ Error merging CV forecasts for {model_name}: {e}")
                continue
        elif isinstance(val_forecast, TimeSeries):
            fig.add_trace(go.Scatter(
                x=val_forecast.time_index,
                y=val_forecast.values().flatten(),
                mode='lines',
                name=f'{model_name} Validation',
                line=dict(color='orange', dash='dot')
            ))
        
        # Find and plot the future forecast
        clean_name = clean_model_name(model_name)
        if clean_name in future_dict:
            future_forecast = future_dict[clean_name]
            print(f"Future forecast time range: {future_forecast.start_time()} - {future_forecast.end_time()}")
            
            # Plot the future forecast
            fig.add_trace(go.Scatter(
                x=future_forecast.time_index,
                y=future_forecast.values().flatten(),
                mode='lines',
                name=f'{clean_name} Future Forecast',
                line=dict(color='blue')
            ))
        
        # Update layout and add the figure
        fig.update_layout(
            title=f"Forecast Plot - {model_name}",
            xaxis_title="Date",
            yaxis_title="Value",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        figures.append(dcc.Graph(figure=fig))
    
    return figures if figures else [html.Div("No forecast plots available. Please check your data and model selection.")]

def plot_residuals(actual_ts, forecast_ts, model_name):
    """
    Create residual plots for a model's forecast(s).
    
    Args:
        actual_ts: The actual time series values (TimeSeries)
        forecast_ts: A single TimeSeries or list of TimeSeries (e.g., from CV)
        model_name: Name of the model
        
    Returns:
        A dash graph component
    """
    print(f"\nCreating residuals plot for {model_name}")

    # Handle cross-validation forecasts
    if isinstance(forecast_ts, list):
        fig = go.Figure()
        for i, forecast_slice in enumerate(forecast_ts):
            if forecast_slice is None or len(forecast_slice) == 0:
                print(f"⚠️ Empty forecast slice at CV fold {i+1}")
                continue

            # Align each slice with actual_ts
            overlap_start = max(actual_ts.start_time(), forecast_slice.start_time())
            overlap_end = min(actual_ts.end_time(), forecast_slice.end_time())
            
            if overlap_start > overlap_end:
                continue
            
            actual_aligned = actual_ts.slice(overlap_start, overlap_end)
            forecast_aligned = forecast_slice.slice(overlap_start, overlap_end)

            if len(actual_aligned) != len(forecast_aligned):
                common_dates = sorted(set(actual_aligned.time_index).intersection(set(forecast_aligned.time_index)))
                if not common_dates:
                    continue

                actual_values = [actual_aligned[date].values()[0][0] for date in common_dates]
                forecast_values = [forecast_aligned[date].values()[0][0] for date in common_dates]
                residuals = np.array(actual_values) - np.array(forecast_values)
                x_vals = common_dates
            else:
                residuals = (actual_aligned - forecast_aligned).values().flatten()
                x_vals = actual_aligned.time_index

            fig.add_trace(go.Scatter(
                x=x_vals,
                y=residuals,
                mode='lines+markers',
                name=f'CV Residual {i+1}',
                opacity=0.6
            ))

        fig.add_shape(
            type="line", x0=min(x_vals), x1=max(x_vals), y0=0, y1=0,
            line=dict(color="red", width=1, dash="dash")
        )

        fig.update_layout(
            title=f"Residuals (CV): {model_name}",
            xaxis_title="Date",
            yaxis_title="Error (Actual - Forecast)"
        )
        return dcc.Graph(figure=fig)

    # Handle single forecast
    elif isinstance(forecast_ts, TimeSeries):
        # Original implementation here (no changes needed)
        actual_start = actual_ts.start_time()
        actual_end = actual_ts.end_time()
        forecast_start = forecast_ts.start_time()
        forecast_end = forecast_ts.end_time()
        
        overlap_start = max(actual_start, forecast_start)
        overlap_end = min(actual_end, forecast_end)
        
        if overlap_start > overlap_end:
            return html.Div(f"No overlapping data between {model_name} forecast and actuals")
        
        actual_aligned = actual_ts.slice(overlap_start, overlap_end)
        forecast_aligned = forecast_ts.slice(overlap_start, overlap_end)
        
        if len(actual_aligned) != len(forecast_aligned):
            common_dates = sorted(set(actual_aligned.time_index).intersection(set(forecast_aligned.time_index)))
            if not common_dates:
                return html.Div(f"No common dates found between actual and forecast for {model_name}")
            actual_values = [actual_aligned[date].values()[0][0] for date in common_dates]
            forecast_values = [forecast_aligned[date].values()[0][0] for date in common_dates]
            residuals = np.array(actual_values) - np.array(forecast_values)
            x_vals = common_dates
        else:
            residuals = (actual_aligned - forecast_aligned).values().flatten()
            x_vals = actual_aligned.time_index

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=residuals,
            mode='lines+markers',
            name='Residuals'
        ))

        fig.add_shape(
            type="line", x0=min(x_vals), x1=max(x_vals), y0=0, y1=0,
            line=dict(color="red", width=1, dash="dash")
        )

        fig.update_layout(
            title=f"Residuals: {model_name}",
            xaxis_title="Date",
            yaxis_title="Error (Actual - Forecast)"
        )
        return dcc.Graph(figure=fig)

    else:
        return html.Div(f"Invalid forecast data type for {model_name}")

def clean_model_name(name):
    """Removes ' (CV)' from model name for matching future forecasts."""
    return name.replace(" (CV)", "").strip()

def normalize_model_name(name):
    return (
        name.replace(" (CV)", "")
            .replace(" (Ensemble)", "")
            .replace(" Future", "")
            .strip()
    )