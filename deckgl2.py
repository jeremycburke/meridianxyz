import streamlit as st
import geopandas as gpd
import pydeck as pdk

# Function to load datasets based on user selection
@st.cache_data  # Cache the data to improve performance
def load_data(dataset_name):
    # if dataset_name == "None":
    #     return gpd.GeoDataFrame()
    if dataset_name == "State Boundaries":
        return gpd.read_parquet(
            r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\03_state_complex.parquet"
        )
    elif dataset_name == "CBSA Boundaries":
        return gpd.read_parquet(
            r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\04_cbsa_complex.parquet"
        )
    elif dataset_name == "CSA Boundaries":
        return gpd.read_parquet(
            r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\05_csa_complex.parquet"
        )
    elif dataset_name == "County Boundaries":
        return gpd.read_parquet(
            r"C:\Users\Jerem\OneDrive\Documents\Git Projects\MeridianXYZ\data\admin_boundaries\processed\geo_complex\06_county_complex.parquet"
        )
    else:
        return gpd.GeoDataFrame()  # Return an empty dataframe if no valid choice is made
    
# Streamlit app title
st.title("Dynamic Regional Visualization")


st.markdown("Compare and contrast different regions of the US against one another to evaluate the alternative investment strategies. Use this information to help you detemine where to invest.")

st.header("Pick Your Boundary for Analysis")

option = st.selectbox(
    "Choose from the dropdown below:",(
        # "None",
        "State Boundaries",
        "CBSA Boundaries",
        "CSA Boundaries",
        "County Boundaries"
     ),
)


# Load the selected dataset
geo_data = load_data(option)

# Convert the GeoDataFrame to GeoJSON format
geojson_data = geo_data.__geo_interface__

# Display the map if a valid dataset is selected
if geo_data.empty:
    st.warning("Please select a dataset from the dropdown above.")
    st.stop()  # Stop the script execution if no valid dataset is selected
else:
    
    # Create a PyDeck layer with the required styling
    
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        get_fill_color="[0, 0, 255, 128]",  # Blue with 50% alpha
        get_line_color=[0, 0, 0],            # Black border
        line_width_min_pixels=1,             # 2pt stroke width
        pickable=True,                       # Enable interactivity for tooltips
    )

    # Create a PyDeck map
    view_state = pdk.ViewState(
        latitude=38.7, #geo_data.geometry.centroid.y.mean(),
        longitude=-97.6, #geo_data.geometry.centroid.x.mean(),
        zoom=3
    )

    # Display the map with PyDeck
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"html": "<b>Region:</b> {NAME}", "style": {"color": "white"}},
    ))
    if option == "CBSA Boundaries":
            expander = st.expander("CBSA explanation")
            expander.write(
                '''
                A core-based statistical area (CBSA) is a U.S. geographic area defined by the Office of Management and Budget (OMB). It contains a large population nucleus, or urban area, and adjacent communities that have a high degree of integration with that nucleus. [reference]](https://en.wikipedia.org/wiki/Core-based_statistical_area)
                ''')
    elif option == "CSA Boundaries":
            expander = st.expander("CSA explanation")
            expander.write('''
                Combined statistical area (CSA) is composed of various combinations of adjacent metropolitan and micropolitan areas with economic ties measured by commuting patterns and demonstrate economic or social linkages.
                           
                The primary distinguishing factor between a CSA and an MSA/μSA is that the social and economic ties between the individual MSAs/μSAs within a CSA are at lower levels than between the counties within an MSA.[3] CSAs represent multiple metropolitan or micropolitan areas that have an employment interchange of at least 15%. CSAs often represent regions with overlapping labor and media markets. [reference](https://en.wikipedia.org/wiki/Combined_statistical_area)
            ''')    
    # elif option == "County Boundaries":
    #         expander = st.expander("See explanation")
    #         expander.write('''
    #             The chart above shows some numbers I picked for you.
    #             I rolled actual dice for these, so they're *guaranteed* to
    #             be random.
    #         ''')
# Display region names as a sidebar list
st.sidebar.header("Regions")
for region_name in geo_data["NAME"]:
    st.sidebar.write(f"• {region_name}")
