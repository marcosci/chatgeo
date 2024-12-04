from openai import OpenAI
import configparser
import sys
import io
import geopandas as gpd
from shapely.geometry import shape
import json
import textwrap

# load config
config = configparser.ConfigParser()
config.read("config.ini")

# use your KEY.
openai_key = config.get("api_key", "openai_key")
client = OpenAI(
    api_key=openai_key,
)


def ask_gis_question(prompt):
    try:
        # Query the ChatGPT API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "A professional Geo-information scientist and programmer good at Python. You have worked on Geographic information science more than 20 years, and know every detail and pitfall when processing spatial data and coding. You know well how to design and implement a function that meet the interface between other functions. Yor program is always robust, considering the various data circumstances, such as colum data types, avoiding mistakes when joining tables, and remove NAN cells before further processing. You have an good feeling of overview, meaning the functions in your program is coherent, and they connect to each other well, such as function names, parameters types, and the calling orders."
                    "Ensure that the final GeoDataFrame or GeoSeries in your code is assigned to the variable 'final_gdf'. "
                    "This variable will always hold the main geospatial result to be extracted.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        # Extract and return the response
        return response
    except Exception as e:
        return str(e)


def execute_python_code(
    code: str, geojson_input: str = None, final_variable_name: str = "final_gdf"
):
    """
    Executes Python code and retrieves the value of a specified variable for geospatial data.

    Args:
        code (str): The Python code to execute.
        geojson_input (str): Optional GeoJSON data as a string (if needed for execution).
        final_variable_name (str): The name of the variable containing geospatial data.

    Returns:
        object: The value of the specified variable.
    """
    # Prepare GeoJSON handling code if input is provided
    geojson_code = f"""
            import geopandas as gpd
            from shapely.geometry import shape
            import json

            # Parse GeoJSON input
            geojson_data = {geojson_input}

            # Create a list of geometries and properties from the GeoJSON features
            geometries = [shape(feature["geometry"]) for feature in geojson_data["features"]]
            properties = [feature["properties"] for feature in geojson_data["features"]]

            # Create a GeoDataFrame from the geometries and properties
            gdf = gpd.GeoDataFrame(properties, geometry=geometries)
            """
    # Combine GeoJSON handling with user-provided code
    full_code = f"{geojson_code}\n{code}"

    # Create a local namespace for executing the code
    ldict = {}

    # Execute the combined code
    exec(full_code, globals(), ldict)

    # Retrieve the result from the local namespace
    result = ldict.get(final_variable_name, None)

    return result
