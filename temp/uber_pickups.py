import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk


st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data

def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache_data)")


st.subheader('Raw data')
st.dataframe(data)

st.subheader('Number of pickups by hour')

hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]

st.bar_chart(hist_values)

# hour_to_filter = st.slider('hour', 0, 23, 17)  # min: 0h, max: 23h, default: 17h
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
# st.subheader(f'Map of all pickups at {hour_to_filter}:00')

# # Create a static map configuration
# map_config = {
#     'zoom': 10,
#     'latitude': 40.722467,
#     'longitude': -73.999429
# }

# # Use pydeck to create a static map with filtered data
# st.pydeck_chart(pdk.Deck(
#     map_style='mapbox://styles/mapbox/light-v9',
#     initial_view_state=pdk.ViewState(
#         latitude=map_config['latitude'],
#         longitude=map_config['longitude'],
#         zoom=map_config['zoom'],
#         pitch=0,
#     ),
#     layers=[
#         pdk.Layer(
#             'ScatterplotLayer',
#             data=filtered_data,
#             get_position='[longitude, latitude]',
#             get_color='[200, 30, 0, 160]',
#             get_radius=100,
#         ),
#     ],
# ))

# import streamlit as st
# import pandas as pd
# import numpy as np
# import pydeck as pdk

# ... existing code ...

hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# Debug: Print the first few rows of filtered_data
# st.write("First few rows of filtered data:")
# st.write(filtered_data.head())

# Ensure the data has the correct columns
if 'lat' in filtered_data.columns and 'lon' in filtered_data.columns:
    map_data = filtered_data[['lat', 'lon']]
else:
    st.error("Data does not contain 'lat' and 'lon' columns")
    st.stop()

# Debug: Print the first few rows of map_data
# st.write("First few rows of map data:")
# st.write(map_data.head())

st.subheader(f'Map of all pickups at {hour_to_filter}:00')

# Use pydeck to create a map with filtered data
st.pydeck_chart(pdk.Deck(
    map_style=None,  # This will use the default map style that matches the site theme
    initial_view_state=pdk.ViewState(
        latitude=40.722467,
        longitude=-73.999429,
        zoom=11,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=map_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=100,
        ),
    ],
))

