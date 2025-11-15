import streamlit as st
import json

from gui_functions import *

st.set_page_config(page_title='Cycle Slip Simulation and Identification', page_icon='images/favicon.png', layout="wide")

col1, col2, _ = st.columns([1,3,1])
with col1:
    st.image('images/favicon.png', width=100)
with col2:
    st.title('Cycle slip simulation and identification')

# sidebar
st.sidebar.title('Simulation Parameters')
st.sidebar.caption('In this section you can provide parameters to simulate the satellite orbit and generate synthetic GNSS data.')

with st.sidebar.expander('Orbit Constants'):
    st.radio('Which orbit constants do you want to use?', options=['Default (SVN 63, PRN 01, Block IIR, 2016-11-28)', 'Upload Custom Almanac File'], index=0, key='almanac_selection')
    if st.session_state.almanac_selection == 'Upload Custom Almanac File':
        st.file_uploader('Upload your own almanac constants file', type=['json'], key='almanac_file')
   
with st.sidebar.expander('Other Parameters'):
    st.radio('How do you want to provide other simulation parameters?', options=['Input Manually', 'Upload Custom Parameters File'], index=0, key='params_selection')
    if st.session_state.params_selection == 'Upload Custom Parameters File':
        st.caption('Below you can find a sample parameters file to use as a template.')
        st.file_uploader('Upload your custom parameters file', type=['json'], key='custom_params_file')
        st.markdown('---')
        st.header('Template for Custom Parameters File')
        st.caption('If you choose to upload a custom parameters file, please ensure it follows the structure below:')
        st.code('''{
    "epochs": 86400,
    "integer_ambiguity": 100,
    "clock_offset_mean": 0.0,
    "clock_offset_std": 1e-03,
    "fundamental_frequency": 10.23,
    "frequency_multiplier_L1": 154,
    "frequency_multiplier_L2": 120,
    "ground_station_latitude": -18.1553985,
    "ground_station_longitude": 49.4098352,
    "ground_station_altitude": 0.0,
    "minimum_elevation_angle": 0.0
}''', language='json')
        if st.session_state.custom_params_file is not None:
            st.success('Custom parameters file uploaded successfully!')
            uploaded_file = st.session_state.custom_params_file
            params_data = json.load(uploaded_file)
            st.session_state.ground_station_latitude = params_data.get('ground_station_latitude', 0.0)
            st.session_state.ground_station_longitude = params_data.get('ground_station_longitude', 0.0)

    elif st.session_state.params_selection == 'Input Manually':
        with open('default_parameters.json', 'r') as file:
            default_params = json.load(file)
        st.subheader('Satellite Parameters')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input('Integer Ambiguity Value', min_value=0, value=default_params.get('integer_ambiguity'), step=1, key='integer_ambiguity')
        with col2:
            st.number_input('Clock Offset Noise Mean', value=default_params.get('clock_offset_mean'), step=0.1, key='clock_offset_noise_mean')
        with col3:
            st.number_input('Clock Offset Noise Standard Deviation', min_value=0.0, value=default_params.get('clock_offset_std'), step=0.1, key='clock_offset_noise_std')
        st.subheader('Frequency Parameters')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input('Fundamental frequency (MHz)', min_value=0.0, value=default_params.get('fundamental_frequency'), step=0.01, key='fundamental_frequency')
        with col2:
            st.number_input('Frequency multiplier for L1', min_value=0, value=default_params.get('frequency_multiplier_L1'), step=1, key='frequency_multiplier_L1')
        with col3:
            st.number_input('Frequency multiplier for L2', min_value=0, value=default_params.get('frequency_multiplier_L2'), step=1, key='frequency_multiplier_L2')
        st.subheader('Ground Station Parameters')
        col1, col2 = st.columns(2)
        with col1:
            st.number_input('Latitude of ground station (degrees)', min_value=-90.0, max_value=90.0, value=default_params.get('ground_station_latitude'), step=0.01, key='ground_station_latitude')
        with col2:
            st.number_input('Longitude of ground station (degrees)', min_value=-180.0, max_value=180.0, value=default_params.get('ground_station_longitude'), step=0.01, key='ground_station_longitude')
        col1, col2 = st.columns(2)
        with col1:
            st.number_input('Altitude of ground station (meters)', min_value=0.0, value=default_params.get('ground_station_altitude'), step=1.0, key='ground_station_altitude')
        with col2:
            st.number_input('Minimum Elevation Angle (degrees)', min_value=0.0, max_value=90.0, value=default_params.get('minimum_elevation_angle'), step=1.0, key='minimum_elevation_angle')
# end sidebar

_, col2, _ = st.columns([1,3,1])
with col2:
    if 'ground_station_latitude' not in st.session_state or 'ground_station_longitude' not in st.session_state:
        st.error('Please provide the ground station parameters')
    else:
        show_map(st.session_state.ground_station_latitude, st.session_state.ground_station_longitude)
        show_computation_button()