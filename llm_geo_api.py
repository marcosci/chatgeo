from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os
from kaldera_kernel import ask_gis_question, execute_python_code
from helper import *

app = FastAPI()

# Input model for the API
class GeoTask(BaseModel):
    task: str
    geojson: dict = None
    model: dict = None

@app.post("/geospatial")
async def analyze_geospatial_task(geo_task: GeoTask):
    """
    Accepts geospatial tasks and processes them using the Solution class.
    """
    try:
        # Instantiate the Solution class with provided parameters
        solution = ask_gis_question(geo_task.task)

        message = solution.choices[0].message.content
        python_code = extract_python_code(message)

        if (python_code != "No Python code found in the response."):
            gis_result = execute_python_code(python_code, geo_task.geojson)

        # Return a success message and optionally, additional outputs
        return {
            "status": "success",
            "prompt": message,
            "python_code": python_code,
            "gis_result": gis_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))