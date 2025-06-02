import shutil

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import os
import glob
from pathlib import Path
import json
from datetime import datetime
import logging
import uvicorn

from api.modeling import load_series_from_csv

app = FastAPI(
    title="CSV to DARTS Time Series Converter",
    description="Convert CSV files to DARTS time series format",
    version="1.0.0"
)
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/forecast")
async def forecast(files: list[UploadFile] = File(...)):
    print("Uploading files...")
    paths = []
    series_list = []
    for file in files:
        # Verify if it's a CSV file
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a CSV file")

        # Save the file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        paths.append(file_path)

        try:
            # Convert to Darts TimeSeries
            time_series = load_series_from_csv(file_path)
            series_list.append(time_series.to_json())
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Error processing {file.filename}: {str(e)}"}
            )

    return {
        "message": "Files uploaded and converted successfully",
        "files": series_list
    }

if __name__ == "__main__":
    uvicorn.run("forecast_api:app", host="0.0.0.0", port=8000, reload=True)


