import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
import pydeck as pdk
import json

# Set Streamlit page configuration to wide mode
# st.set_page_config(layout="wide")

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

def load_comparative_data():
    comparative_data = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\combined_clusters.parquet"
    )

    return comparative_data

comparative_data = load_comparative_data()

@st.cache_data
def load_df():
    age_and_sex = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_age_and_sex.parquet"
    )
    commute = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_commute.parquet"
    )
    computers_and_internet = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_computers_and_internet.parquet"
    )
    education = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_education.parquet"
    )
    employment = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_employement.parquet"
    )
    housing = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_housing.parquet"
    )
    income_and_earnings = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_income_and_earnings.parquet"
    )
    poverty = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_poverty.parquet"
    )
    race_and_hispanic_origin = gpd.read_parquet(
        r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\notebooks\database_building\variables_race_and_hispanic_origin.parquet"
    )
    return age_and_sex, commute, computers_and_internet, education, employment, housing, income_and_earnings, poverty, race_and_hispanic_origin

age_and_sex, commute, computers_and_internet, education, employment, housing, income_and_earnings, poverty, race = load_df()

# Streamlit app title
st.title("Meridian XYZ")
st.header("National Real Estate Analysis Tool")
st.markdown(
    '''
    Use this tool to analyze and compare different regions of the US to evaluate alternative investment strategies. Use this information to help you determine where to invest.

    The tools uses a combination of geospatial data and demographic data to provide insights into different regions of the US. The tool allows you to input an address and see which region the address falls within. The tool also allows you to compare different regions based on demographic data.
    '''
)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Administrative Boundaries")
    st.markdown('''
    - The tool uses the following boundaries:
    - State Boundaries
    - CBSA Boundaries
    - County Boundaries
    - Tract Boundaries
    - Block Group Boundaries
''')

with col2:
    st.subheader("Data Sets")
    st.markdown('''
    - Age and Sex
    - Commute Time to Work
    - Computers and Internet Usage at Home
    - Education Level Attained
    - Employment Status
    - Housing Characteristics
    - Income and Earnings
    - Poverty
    - Race and Hispanic Origin
''')

# User input for address
st.header("Search for an Address")
# Assuming address is obtained from user input
address = st.text_input("Enter an address:")

if not address:
    st.write("Please enter an address to see the results.")
    location = None
else:
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
    else:
        st.error("Could not geocode the address. Please try again.")

# Plot Comparative Map with Filter
comparative_data_json = json.loads(comparative_data.to_json())

#########################
# Comparative Map
#########################
if location:
    # Define a function to map the "overall_cluster" value to a color
    # Define a function to map cluster values to colors
    def get_fill_color(cluster_value):
        color_map = {
            0: [255, 0, 0, 50],   # Red with transparency
            1: [0, 255, 0, 50],   # Green with transparency
            2: [0, 0, 255, 50],   # Blue with transparency
            3: [255, 255, 0, 50], # Yellow with transparency
            4: [255, 165, 0, 50], # Orange with transparency
            5: [128, 0, 128, 50], # Purple with transparency
            6: [0, 255, 255, 50], # Cyan with transparency
            7: [255, 192, 203, 50], # Pink with transparency
            8: [128, 128, 128, 50], # Gray with transparency
            9: [0, 128, 0, 50],   # Dark Green with transparency
        }
        return color_map.get(cluster_value, [255, 255, 255, 50])  # Default to white with transparency if not found

    # Dropdown to select the variable to display
    variable_options = [
        "overall_cluster",
        "age_and_sex_cluster",
        "commute_cluster",
        "computers_and_internet_cluster",
        "education_cluster",
        "employment_cluster",
        "housing_cluster",
        "income_and_earnings_cluster",
        "poverty_cluster",
        "race_cluster"
    ]

    selected_variable = st.selectbox("Select variable to display:", variable_options)

    # Add the fill color to the GeoJSON features based on the selected variable
    for feature in comparative_data_json['features']:
        cluster_value = feature['properties'].get(selected_variable, -1)
        feature['properties']['fill_color'] = get_fill_color(cluster_value)

    # Create a list of unique clusters for the selected variable
    unique_clusters = sorted(comparative_data[selected_variable].unique())

    # Create a multiselect widget for clusters
    selected_clusters = st.multiselect(
        "Select clusters to display:",
        options=unique_clusters,
        default=unique_clusters
    )

    # Filter the GeoJSON features based on selected clusters
    filtered_features = [
        feature for feature in comparative_data_json['features']
        if feature['properties'].get(selected_variable) in selected_clusters
    ]

    # Update the GeoJSON with filtered features
    comparative_data_json['features'] = filtered_features

    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=[{"coordinates": [location.longitude, location.latitude]}],
        get_position="coordinates",
        get_color=[255, 0, 0],
        get_radius=50,
        radius_min_pixels=5,
        radius_max_pixels=1000,
    )

    polygon_comparative_data_layer = pdk.Layer(
        "GeoJsonLayer",
        comparative_data_json,
        get_fill_color="properties.fill_color",
        get_line_color=[255, 255, 255],  # Black border
        line_width_min_pixels=.5,
        pickable=True,
    )

    # Define the initial view state for the map
    if address and location:
        view_state = pdk.ViewState(
            latitude=location.latitude,
            longitude=location.longitude,
            zoom=12,
        )
    else:
        view_state = pdk.ViewState(
            latitude=39.23,  # Default latitude (e.g., San Francisco)
            longitude=-97.36,  # Default longitude
            zoom=3,  # Default zoom level
        )

    # Display the PyDeck map
    st.pydeck_chart(
        pdk.Deck(
            layers=[polygon_comparative_data_layer],
            initial_view_state=view_state,
            tooltip={"html": f"<b>Region:</b> {{NAME}}<br><b>Cluster:</b> {{{selected_variable}}}", "style": {"color": "white"}},
            map_style='mapbox://styles/mapbox/light-v10'  # Set the map style to light
        )
    )
    st.subheader("Cluster Distribution of: " f"***{selected_variable}***")
    st.bar_chart(comparative_data[selected_variable].value_counts())

    st.header("Data Tables")

    expander_age_and_sex = st.expander("Age and Sex Data")
    expander_age_and_sex.dataframe(age_and_sex)

    expander_comparative_data = st.expander("Comparative Data")
    expander_comparative_data.dataframe(comparative_data)

    expander_commute_data = st.expander("Commute Data")
    expander_commute_data.dataframe(commute)

    expander_computers_and_internet_data = st.expander("Computers and Internet Data")
    expander_computers_and_internet_data.dataframe(computers_and_internet)

    expander_education_data = st.expander("Education Data")
    expander_education_data.dataframe(education)

    expander_employment_data = st.expander("Employment Data")
    expander_employment_data.dataframe(employment)

    expander_housing_data = st.expander("Housing Data")
    expander_housing_data.dataframe(housing)

    expander_income_and_earnings_data = st.expander("Income and Earnings Data")
    expander_income_and_earnings_data.dataframe(income_and_earnings)

    expander_poverty_data = st.expander("Poverty Data")
    expander_poverty_data.dataframe(poverty)

    expander_race_data = st.expander("Race Data")
    expander_race_data.dataframe(race)

else:
    ()# st.error("Could not geocode the address. Please try again.")