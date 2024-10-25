#%%
import requests
import zipfile
import io
import geopandas as gpd
import pyarrow.parquet as pq
import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import pydeck as pdk
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Polygon, MultiPolygon

# #%%
# def download_tiger_msa_data(year=2022, output_path="msa_data.shp"):
#     """
#     Downloads and extracts TIGER/Line shapefiles for Metropolitan/Micropolitan Statistical Areas.
    
#     Args:
#         year (int): The year of the TIGER data. Defaults to 2022.
#         output_path (str): Path to save the extracted shapefile.
        
#     Returns:
#         gdf (GeoDataFrame): A GeoDataFrame containing the MSA/MicroSA geometries.
#     """
#     # Construct the correct URL based on known patterns
#     base_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CBSA/"
#     zip_filename = f"tl_{year}_us_cbsa.zip"
#     url = f"{base_url}{zip_filename}"
    
#     print(f"Attempting to download: {url}")
    
#     # Download the ZIP file
#     response = requests.get(url)
#     if response.status_code == 404:
#         raise Exception(f"Data for the year {year} not found. Check the URL or try a different year.")
#     elif response.status_code != 200:
#         raise Exception(f"Failed to download data. Status code: {response.status_code}")
    
#     # Extract the ZIP content
#     with zipfile.ZipFile(io.BytesIO(response.content)) as z:
#         z.extractall("msa_data")  # Extract to a directory called 'msa_data'
    
#     # Load the shapefile into a GeoDataFrame
#     shapefile_path = f"msa_data/tl_{year}_us_cbsa.shp"
#     gdf = gpd.read_file(shapefile_path)
    
#     # Optionally, save the data to a new shapefile
#     gdf.to_file(output_path)
#     print(f"Shapefile saved to {output_path}")
    
#     return gdf


# #%%
# # Example usage
# gdf = download_tiger_msa_data(year=2024)
# gdf.head()

# #%%
# gdf = gpd.GeoDataFrame(gdf, crs="EPSG:4326", geometry="geometry")
# gdf = gdf.drop(['CSAFP',
#                'CBSAFP',
#                'GEOID',
#                'GEOIDFQ',
#                'NAMELSAD',
#                'LSAD',
#                'MEMI',
#                'MTFCC',
#                'ALAND',
#                'AWATER',	
#                'INTPTLAT',
#                'INTPTLON'], axis=1)
# #%%
# gdf.to_parquet("data/processed/tiger.parquet")
#%%
gdf=gpd.read_parquet("data/processed/tiger.parquet")
gdf = gpd.GeoDataFrame(gdf, crs="EPSG:4326", geometry="geometry")
# gdf = gdf[0:50]
# gdf

#%%
# gdf = gdf.loc[gdf.geometry.geometry.type!='MultiPolygon']

# Function to explode MultiPolygons into individual Polygons
def explode_multipolygons(geodataframe):
    """Convert MultiPolygons into individual Polygons."""
    gdf_exploded = geodataframe.explode(ignore_index=True)
    gdf_exploded["geometry"] = gdf_exploded["geometry"].apply(lambda x: x if x.geom_type == "Polygon" else None)
    return gdf_exploded.dropna(subset=["geometry"])

#%%
# Apply the function to convert MultiPolygon geometries
gdf = explode_multipolygons(gdf)
#%%
gdf["geometry"] = gdf["geometry"].simplify(0.01, preserve_topology=True)
gdf


#%%
gdf["coordinates"] = gdf["geometry"].apply(lambda geom: list(geom.exterior.coords) 
                                            if geom.geom_type == "Polygon" 
                                            else [list(poly.exterior.coords) for poly in geom])

gdf = gdf.drop(['geometry'], axis=1)

#%%
gdf = pd.read_parquet("data/processed/cbsa_vis.parquet")

gdf
# %%
polygon_layer = pdk.Layer(
    "SolidPolygonLayer",
    data=gdf,
    get_polygon="coordinates",  # column name containing polygon coordinates
    opacity=.8,
    stroked=True,
    filled=True,
    extruded=True,
    get_elevation=5000,
    get_fill_color=[255, 0, 0, 100],  # RGBA color (semi-transparent red)
    get_line_color=[255, 255, 255],  # RGB color for polygon outline
    line_width_min_pixels=1,
    pickable=True,
    # auto_highlight=True,
)

# Set the view state
view_state = pdk.ViewState(
    latitude = 39.009486,
    longitude = -97.960754,
    zoom=3,
    pitch=0
)

# Create the deck
deck = pdk.Deck(
    layers=[polygon_layer],
    initial_view_state=view_state,
    tooltip={"text": "{NAME}"}  # Assumes your GeoDataFrame has a 'name' column
)

st.pydeck_chart(deck)
# %%
