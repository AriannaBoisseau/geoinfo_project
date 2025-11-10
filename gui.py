import streamlit as st
import json

from gui_functions import *

st.title('Cycle slip simulation and identification')

st.header('Simulation parameters')
st.caption('In this section you can provide parameters to simulate the satellite orbit and generate synthetic GNSS data.')

st.subheader('Almanac Constants')
st.caption('The almanac constants define the approximate orbit of a satellite.')
st.radio('Which almanac constants do you want to use?', options=['Default (SVN 63, PRN 01, Block IIR, 2016-11-28)', 'Upload Custom Almanac File'], index=0, key='almanac_selection')
if st.session_state.almanac_selection == 'Upload Custom Almanac File':
    st.file_uploader('Upload your own almanac constants file', type=['json'], key='almanac_file')

st.subheader('Other Parameters')
st.caption('Provide other parameters for the simulation.')
st.radio('How do you want to provide other simulation parameters?', options=['Input Manually', 'Upload Custom Parameters File'], index=0, key='params_selection')
if st.session_state.params_selection == 'Upload Custom Parameters File':
    st.file_uploader('Upload your custom parameters file', type=['json'], key='custom_params_file')
    # If a file is uploaded, read and display parameters
    if st.session_state.custom_params_file is not None:        
        st.success('Custom parameters file uploaded successfully!')
        uploaded_file = st.session_state.custom_params_file
        params_data = json.load(uploaded_file)

        show_map(params_data.get('ground_station_latitude'), params_data.get('ground_station_longitude'))

        show_computation_button()
   

elif st.session_state.params_selection == 'Input Manually':
    with open('default_parameters.json', 'r') as file:
        default_params = json.load(file)
    st.number_input('Integer Ambiguity Value', min_value=0, value=default_params.get('integer_ambiguity'), step=1, key='integer_ambiguity')
    st.number_input('Clock Offset Noise Mean', value=default_params.get('clock_offset_mean'), step=0.1, key='clock_offset_noise_mean')
    st.number_input('Clock Offset Noise Standard Deviation', min_value=0.0, value=default_params.get('clock_offset_std'), step=0.1, key='clock_offset_noise_std')
    st.number_input('Fundamental frequency of satellite clock (MHz)', min_value=0.0, value=default_params.get('fundamental_frequency'), step=0.01, key='fundamental_frequency')
    st.number_input('Frequency multiplier for L1', min_value=0, value=default_params.get('frequency_multiplier_L1'), step=1, key='frequency_multiplier_L1')
    st.number_input('Frequency multiplier for L2', min_value=0, value=default_params.get('frequency_multiplier_L2'), step=1, key='frequency_multiplier_L2')
    st.number_input('Latitude of ground station (degrees)', min_value=-90.0, max_value=90.0, value=default_params.get('ground_station_latitude'), step=0.01, key='ground_station_latitude')
    st.number_input('Longitude of ground station (degrees)', min_value=-180.0, max_value=180.0, value=default_params.get('ground_station_longitude'), step=0.01, key='ground_station_longitude')
    st.number_input('Altitude of ground station (meters)', min_value=0.0, value=default_params.get('ground_station_altitude'), step=1.0, key='ground_station_altitude')
    st.number_input('Minimum Elevation Angle (degrees)', min_value=0.0, max_value=90.0, value=default_params.get('minimum_elevation_angle'), step=1.0, key='minimum_elevation_angle')

    show_map(st.session_state.ground_station_latitude, st.session_state.ground_station_longitude)

    show_computation_button()