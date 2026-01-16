import streamlit as st
import json
from gui_functions import *

def render_sidebar():
    st.session_state.sidebar_state = 'expanded'

    if 'input_method' not in st.session_state:
        st.session_state.input_method = 'Not Selected'

    with st.sidebar:
        st.sidebar.title('Simulation Parameters')
        st.sidebar.caption('In this section you can provide parameters to simulate the satellite orbit and generate synthetic GNSS data.')
        
        # reset button
        if 'input_method' in st.session_state and st.session_state.input_method != 'Not Selected':
            if st.button('Change Input Method (all parameters will be lost)', width='stretch'):
                for key in list(st.session_state.keys()):
                    if key not in ['sidebar_state']:
                        del st.session_state[key]
                st.session_state.input_method = 'Not Selected'
                st.rerun()

        if st.session_state.input_method == 'Not Selected':
            st.header('How do you want to provide the simulation parameters?')
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Enter Manually', width='stretch'):
                    st.session_state.input_method = 'Enter Manually'
                    st.rerun()
            with col2:
                if st.button('Upload Custom Parameters File', width='stretch'):
                    st.session_state.input_method = 'Upload Custom Parameters File'
                    st.rerun()

        elif st.session_state.input_method == 'Upload Custom Parameters File':
            st.file_uploader('Upload your own parameters file', type=['json'], key='manual_params_file')
            if st.session_state.manual_params_file is not None:
                st.success('Custom parameters file uploaded successfully!')
            
            st.markdown('---')
            st.header('Template for Parameters File')
            st.caption('If you choose to upload a custom parameters file, please ensure it follows the structure below:')
            with open('default_parameters.json', 'r') as file:
                code = file.read()
            st.code(code, language='json')

            # parsing file
            if st.session_state.manual_params_file is not None:
                uploaded_file = st.session_state.manual_params_file
                params_data = json.load(uploaded_file)
                # TODO: aggiungere controllo su ogni parametro
                st.session_state.ground_station_latitude = params_data.get('ground_station_latitude', 0.0)
                st.session_state.ground_station_longitude = params_data.get('ground_station_longitude', 0.0)

        elif st.session_state.input_method == 'Enter Manually':
            if st.session_state.get('computation_running') == True:
                st.session_state.expand_satellite_params = False
                st.session_state.expand_frequency_params = False
                st.session_state.expand_ground_station_params = False
                st.session_state.expand_other_params = False
                st.session_state.expand_cycle_slip_params = False

            with open('default_parameters.json', 'r') as file:
                default_params = json.load(file)
            with st.expander('Satellite Parameters', expanded=st.session_state.get('expand_satellite_params', True)):
                st.subheader('Keplerian Orbit Parameters')
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input('Eccentricity', min_value=None, max_value=None, value=default_params.get('e'), step=None, format='%e')
                with col2:
                    st.number_input('Sqrt of semi-major axis', min_value=None, max_value=None, value=default_params.get('sqrt_a'), step=None, format='%e')
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input('Mean Anomaly', min_value=None, max_value=None, value=default_params.get('M0'), step=None, format='%e')
                with col2:
                    st.number_input('Longitude of the ascending node', min_value=None, max_value=None, value=default_params.get('Omega0'), step=None, format='%e')
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input('Rate of node\'s right ascension', min_value=None, max_value=None, value=default_params.get('Omegadot'), step=None, format='%e')
                with col2:
                    st.number_input('Inclination', min_value=None, max_value=None, value=default_params.get('i0'), step=None, format='%e')
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input('Rate of inclination angle', min_value=None, max_value=None, value=default_params.get('idot'), step=None, format='%e')
                with col2:
                    st.number_input('Argument of perigee', min_value=None, max_value=None, value=default_params.get('w0'), step=None, format='%e')
                col1, col2 = st.columns(2)
                st.number_input('Rate of argument of perigee', min_value=None, max_value=None, value=default_params.get('wdot'), step=None, format='%e')
                st.subheader('Other Satellite Parameters')
                st.number_input('Integer Ambiguity Value', min_value=0, value=default_params.get('integer_ambiguity'), step=1, key='integer_ambiguity')

            with st.expander('Frequency Parameters', expanded=st.session_state.get('expand_frequency_params', True)):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.number_input('Fundamental frequency (Hz)', min_value=0.0, value=default_params.get('fundamental_frequency'), step=0.01, key='fundamental_frequency', format='%e')
                with col2:
                    st.number_input('Frequency multiplier for L1', min_value=0, value=default_params.get('frequency_multiplier_L1'), step=1, key='frequency_multiplier_L1')
                with col3:
                    st.number_input('Frequency multiplier for L2', min_value=0, value=default_params.get('frequency_multiplier_L2'), step=1, key='frequency_multiplier_L2')
                
            with st.expander('Ground Station Parameters', expanded=st.session_state.get('expand_ground_station_params', True)):
                st.subheader('Clock Offset')
                st.number_input('dt0', min_value=None, max_value=None, value=default_params.get('dt0'), step=None, format='%e')
                st.number_input('dt1', min_value=None, max_value=None, value=default_params.get('dt1'), step=None, format='%e') 
                st.number_input('dt2', min_value=None, max_value=None, value=default_params.get('dt2'), step=None, format='%e') 
                st.number_input('Clock Offset Noise Standard Deviation', min_value=0.0, value=default_params.get('clock_offset_std'), step=None, key='clock_offset_noise_std', format='%e')
                st.subheader('Position')
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

            with st.expander('Other Simulation Parameters', expanded=st.session_state.get('expand_other_params', True)):
                st.number_input('Simulation Duration (seconds)', min_value=1, value=default_params.get('epochs'), step=1, key='epochs')
                st.number_input('Earth\'s Standard Gravitational Parameter', min_value=None, max_value=None, value=default_params.get('GMe'), step=None, format='%e', key='GMe')
                st.number_input('Earth\'s Angular Velocity', min_value=None, max_value=None, value=default_params.get('OmegaEdot'), step=None, format='%e', key='OmegaEdot')

            # TODO add klobuchar parameters

            with st.expander('Cycle Slip Parameters', expanded=st.session_state.get('expand_cycle_slip_params', True)):
                st.number_input('epoch of cycle slip', min_value=0, max_value=st.session_state.epochs-1, value=0, step=1, key='cycle_slip_epoch')

        else:
            st.error('An unexpected error occurred. Please refresh the page and try again.')