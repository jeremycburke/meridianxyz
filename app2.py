#%%
import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import pydeck as pdk
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Polygon, MultiPolygon

import os


import matplotlib.pyplot as plt

from typing import Optional

import censusdis.data as ced
import censusdis.maps as cem
import censusdis.values as cev
import censusdis.geography as cgeo
from censusdis import states
from censusdis.values import ALL_SPECIAL_VALUES




# The year we want data for.
YEAR = 2021
DATASET = "acs/acs5"
MEDIAN_HOUSEHOLD_INCOME_VARIABLE = "B19013_001E"
VARIABLES = ["NAME", MEDIAN_HOUSEHOLD_INCOME_VARIABLE]

reader = cem.ShapeReader(year=YEAR)

gdf_state_bounds = reader.read_cb_shapefile("us", "state")
gdf_state_bounds = gdf_state_bounds[
    gdf_state_bounds["STATEFP"].isin(states.ALL_STATES_AND_DC)
]

gdf = ced.download(
    DATASET,
    YEAR,
    VARIABLES,
    metropolitan_statistical_area_micropolitan_statistical_area="*",
    with_geometry=True,
)

# #%%
# file_path = "data/processed/test.gpkg"
# gdf = gpd.read_file(file_path, engine="pyogrio")
# # chart_data[:10].to_file("data/processed/test_small.gpkg", driver="GPKG")

# gdf

def explode_multipolygons(geodataframe):
    """Convert MultiPolygons into individual Polygons."""
    gdf_exploded = geodataframe.explode(ignore_index=True)
    gdf_exploded["geometry"] = gdf_exploded["geometry"].apply(lambda x: x if x.geom_type == "Polygon" else None)
    return gdf_exploded.dropna(subset=["geometry"])

gdf = explode_multipolygons(gdf)

gdf["geometry"] = gdf["geometry"].simplify(0.01, preserve_topology=True)
# gdf




#%%
# gdf = gpd.GeoDataFrame(gdf, crs="EPSG:4326", geometry="geometry")
gdf = gdf.to_crs("EPSG:4326")
# gdf

# gdf["coordinates"] = gdf["geometry"].apply(
#     lambda geom: list(geom.exterior.coords) 
#     if geom.geom_type == "Polygon" 
#     else [list(poly.exterior.coords) for poly in geom.geoms])

# Ensure all polygons have closed rings (first and last coordinates must match)
# def close_ring(coords):
#     if coords[0] != coords[-1]:
#         coords.append(coords[0])  # Close the ring by adding the first coordinate at the end
#     return coords

# Convert the geometry column to lists of closed coordinates
# gdf["coordinates"] = gdf["geometry"].apply(
#     lambda geom: [close_ring(list(poly.exterior.coords)) for poly in geom.geoms]
#     if geom.geom_type == "MultiPolygon"
#     else close_ring(list(geom.exterior.coords))
# )

# Inspect the data to ensure coordinates are correct
# gdf.head()



#%%
lat = gdf.geometry.centroid.y.mean()
lon = gdf.geometry.centroid.x.mean()

 #%%
# Create the SolidPolygonLayer
polygon_layer = pdk.Layer(
    "SolidPolygonLayer",
    data=gdf,
    get_polygon="geometry",  # column name containing polygon coordinates
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
    latitude = lat,
    longitude = lon,
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
# gdf
# %%
