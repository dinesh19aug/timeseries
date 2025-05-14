import pandas as pd
import base64
import io

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    df['date'] = pd.to_datetime(df['date'])
    return df