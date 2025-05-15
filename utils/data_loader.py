import pandas as pd
import base64
import io


def parse_csv_contents(contents):
    """
    Parses the base64-encoded CSV file content uploaded via Dash Upload component.
    Returns a pandas DataFrame with parsed date column.
    """
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    # Standardize column names (in case)
    df.columns = df.columns.str.strip().str.lower()

    # Ensure expected columns
    if 'date' not in df.columns or 'value' not in df.columns:
        raise ValueError("CSV must contain 'date' and 'value' columns.")

    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df