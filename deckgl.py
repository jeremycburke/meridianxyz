import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import pydeck as pdk

# chart_data = gpd.read_file(r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\01_region_complex.geojson")

# print(chart_data[:10])

# st.pydeck_chart(
#     pdk.Deck(
#         map_style=None,
#         initial_view_state=pdk.ViewState(
#             latitude=37.76,
#             longitude=-122.4,
#             zoom=3,
#             pitch=0,
#         ),
#         layers=[
#             pdk.Layer(
#                 "GeoJsonLayer",
#                 data=chart_data,
#                 get_position="[lon, lat]",
#                 radius=200,
#                 elevation_scale=4,
#                 elevation_range=[0, 1000],
#                 pickable=True,
#                 extruded=True,
#             ),
#         ],
#     )
# )

chart_data = gpd.read_file(r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\01_region_complex.geojson")

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=37.76,
            longitude=-122.4,
            zoom=3,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "GeoJsonLayer",
                data=chart_data,
                get_position="[lon, lat]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                get_fill_color='[0, 0, 255, 128]',  # Blue fill with 50% opacity
                get_line_color=[0, 0, 0],  # Black stroke
                extruded=True,
                stroked=True,  # Enable polygon outlines
                filled=True,   # Ensure polygons are filled
            ),
            pdk.Layer(
                "TextLayer",
                data=chart_data,
                get_position="[lon, lat]",
                get_text="name",  # Assuming 'name' is the field in your data containing region names
                get_size=16,
                get_color=[0, 0, 0],  # Black text
                get_angle=0,
                get_alignment_baseline="'bottom'",
            ),
        ],
    )
)