import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
import pydeck as pdk
import json

# Set Streamlit page configuration to wide mode
st.set_page_config(layout="wide")

# Load your GeoDataFrame with the block group polygons

# Load multiple GeoDataFrames with different boundary polygons
@st.cache_data  # Cache the data for better performance
def load_data():
    state_data = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\03_state_complex.parquet"
    )
    cbsa_data = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\04_cbsa_complex.parquet"
    ) 
    county_data = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\06_county_complex.parquet"
    )
    tract_data = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\07_tract_complex.parquet"
    )
    block_data = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\08_blockgroup_complex.parquet"
    )
    return state_data, cbsa_data, county_data, tract_data, block_data

state_data, cbsa_data, county_data, tract_data, block_data = load_data()

# Streamlit app title
st.title("Check if Address is Within a Block Group")

# User input for address
address = st.text_input("Enter an address:")



# Geolocate the address using geopy
if address:
    geolocator = Nominatim(user_agent="streamlit_geocoder")
    location = geolocator.geocode(address)

    if location:
        # Create a Point object for the address location
        address_point = Point(location.longitude, location.latitude)

        # Check if the point is within any polygon in the GeoDataFrame
        matching_state = state_data[state_data.contains(address_point)]
        matching_cbsa = cbsa_data[cbsa_data.contains(address_point)]
        matching_county = county_data[county_data.contains(address_point)]
        matching_tract = tract_data[tract_data.contains(address_point)]
        matching_block_group = block_data[block_data.contains(address_point)]

        # Calculate statistics for each matching geometry
        def calculate_statistics(geometry):
            return {
                "Area": geometry.area,
                "Perimeter": geometry.length
            }        

        if not matching_block_group.empty:
            st.success(f"The address is within: {matching_block_group.iloc[0]['NAME']}")
        else:
            st.warning("The address is not within any admin boundary in the data.")

        # Visualize the address and the polygons on the map
        matching_state_json = json.loads(matching_state.to_json())
        matching_cbsa_json = json.loads(matching_cbsa.to_json())
        matching_county_json = json.loads(matching_county.to_json())
        matching_tract_json = json.loads(matching_tract.to_json())
        matching_block_group_json = json.loads(matching_block_group.to_json())

        # PyDeck layers for block group polygons and address point
        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=[{"coordinates": [location.longitude, location.latitude]}],
            get_position="coordinates",
            get_color=[255, 0, 0],
            get_radius=50,
            radius_min_pixels=5,
            radius_max_pixels=1000,
        )

        polygon_state_layer = pdk.Layer(
            "GeoJsonLayer",
            matching_state_json,
            get_fill_color=[0, 0, 255, 50], # Blue with transparency
            get_line_color=[255, 255, 255],# Black border
            line_width_min_pixels=.5,
            pickable=True,
        )

        polygon_cbsa_layer = pdk.Layer(
            "GeoJsonLayer",
            matching_cbsa_json,
            get_fill_color=[0, 0, 255, 50],  # Blue with transparency
            get_line_color=[255, 255, 255],            # Black border
            line_width_min_pixels=.5,
            pickable=True,
        )

        polygon_county_layer = pdk.Layer(
            "GeoJsonLayer",
            matching_county_json,
            get_fill_color=[0, 0, 255, 50],  # Blue with transparency
            get_line_color=[255, 255, 255],            # Black border
            line_width_min_pixels=.5,
            pickable=True,
        )

        polygon_tract_layer = pdk.Layer(
            "GeoJsonLayer",
            matching_tract_json,
            get_fill_color=[0, 0, 255, 50],  # Blue with transparency
            get_line_color=[255, 255, 255],            # Black border
            line_width_min_pixels=.5,
            pickable=True,
        )

        polygon_block_group_layer = pdk.Layer(
            "GeoJsonLayer",
            matching_block_group_json,
            get_fill_color=[0, 0, 255, 50],  # Blue with transparency
            get_line_color=[255, 255, 255],            # Black border
            line_width_min_pixels=.5,
            pickable=True,
        )

        # Define the initial view state for the map
        view_state = pdk.ViewState(
            latitude=location.latitude,
            longitude=location.longitude,
            zoom=12,
        )

        # Display the PyDeck map
        st.pydeck_chart(
            pdk.Deck(
            layers=[polygon_state_layer, polygon_cbsa_layer, polygon_county_layer, polygon_tract_layer, polygon_block_group_layer, point_layer],
            initial_view_state=view_state,
            tooltip={"html": "<b>Region:</b> {NAME}", "style": {"color": "white"}},
            map_style='mapbox://styles/mapbox/light-v10'  # Set the map style to light
            )
        )
        state_stats = matching_state.geometry.apply(calculate_statistics).to_list()
        cbsa_stats = matching_cbsa.geometry.apply(calculate_statistics).to_list()
        county_stats = matching_county.geometry.apply(calculate_statistics).to_list()
        tract_stats = matching_tract.geometry.apply(calculate_statistics).to_list()
        block_group_stats = matching_block_group.geometry.apply(calculate_statistics).to_list()

        # Display statistics in the Streamlit app
        st.subheader("Statistics for Matching Geometries")
        if state_stats:
            st.text(f"State Statistics: {state_stats}")
        if cbsa_stats:
            st.text(f"CBSA Statistics: {cbsa_stats}")
        if county_stats:
            st.text(f"County Statistics: {county_stats}")
        if tract_stats:
            st.text(f"Tract Statistics: {tract_stats}")
        if block_group_stats:
            st.text(f"Block Group Statistics: {block_group_stats}")
    else:
        st.error("Could not geocode the address. Please try again.")

       