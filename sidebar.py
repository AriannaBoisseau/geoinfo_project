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
                uploaded_file.seek(0)
                params_data = json.load(uploaded_file)
                st.session_state['params_data'] = params_data

        elif st.session_state.input_method == 'Enter Manually':
            if st.session_state.get('computation_running') == True:
                st.session_state.expand_satellite_params = False
                st.session_state.expand_frequency_params = False
                st.session_state.expand_ground_station_params = False
                st.session_state.expand_other_params = False
                st.session_state.expand_cycle_slip_params = False
                st.session_state.expand_klobuchar_params = False

            with open('default_parameters.json', 'r') as file:
                default_params = json.load(file)
            
            # Initialize params_data if not exists
            if 'params_data' not in st.session_state:
                st.session_state['params_data'] = default_params.copy()

            with st.expander('Satellite Parameters', expanded=st.session_state.get('expand_satellite_params', True)):
                st.subheader('Keplerian Orbit Parameters')
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state['params_data']['e'] = st.number_input('Eccentricity', min_value=None, max_value=None, value=st.session_state['params_data'].get('e', 0.0), step=None, format='%e')
                with col2:
                    st.session_state['params_data']['sqrt_a'] = st.number_input('Sqrt of semi-major axis', min_value=None, max_value=None, value=st.session_state['params_data'].get('sqrt_a', 0.0), step=None, format='%e')
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state['params_data']['M0'] = st.number_input('Mean Anomaly', min_value=None, max_value=None, value=st.session_state['params_data'].get('M0', 0.0), step=None, format='%e')
                with col2:
                    st.session_state['params_data']['Omega0'] = st.number_input('Longitude of the ascending node', min_value=None, max_value=None, value=st.session_state['params_data'].get('Omega0', 0.0), step=None, format='%e')
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state['params_data']['Omegadot'] = st.number_input('Rate of node\'s right ascension', min_value=None, max_value=None, value=st.session_state['params_data'].get('Omegadot', 0.0), step=None, format='%e')
                with col2:
                    st.session_state['params_data']['i0'] = st.number_input('Inclination', min_value=None, max_value=None, value=st.session_state['params_data'].get('i0', 0.0), step=None, format='%e')
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state['params_data']['idot'] = st.number_input('Rate of inclination angle', min_value=None, max_value=None, value=st.session_state['params_data'].get('idot', 0.0), step=None, format='%e')
                with col2:
                    st.session_state['params_data']['w0'] = st.number_input('Argument of perigee', min_value=None, max_value=None, value=st.session_state['params_data'].get('w0', 0.0), step=None, format='%e')
                col1, col2 = st.columns(2)
                st.session_state['params_data']['wdot'] = st.number_input('Rate of argument of perigee', min_value=None, max_value=None, value=st.session_state['params_data'].get('wdot', 0.0), step=None, format='%e')
                st.subheader('Other Satellite Parameters')
                st.session_state['params_data']['integer_ambiguity'] = st.number_input('Integer Ambiguity Value', min_value=0, value=st.session_state['params_data'].get('integer_ambiguity', 0), step=1)

            with st.expander('Frequency Parameters', expanded=st.session_state.get('expand_frequency_params', True)):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.session_state['params_data']['fundamental_frequency'] = st.number_input('Fundamental frequency (Hz)', min_value=0.0, value=st.session_state['params_data'].get('fundamental_frequency', 0.0), step=0.01, format='%e')
                with col2:
                    st.session_state['params_data']['frequency_multiplier_L1'] = st.number_input('Frequency multiplier for L1', min_value=0, value=st.session_state['params_data'].get('frequency_multiplier_L1', 0), step=1)
                with col3:
                    st.session_state['params_data']['frequency_multiplier_L2'] = st.number_input('Frequency multiplier for L2', min_value=0, value=st.session_state['params_data'].get('frequency_multiplier_L2', 0), step=1)
                
            with st.expander('Ground Station Parameters', expanded=st.session_state.get('expand_ground_station_params', True)):
                st.subheader('Clock Offset')
                st.session_state['params_data']['dt0'] = st.number_input('dt0', min_value=None, max_value=None, value=st.session_state['params_data'].get('dt0', 0.0), step=None, format='%e')
                st.session_state['params_data']['dt1'] = st.number_input('dt1', min_value=None, max_value=None, value=st.session_state['params_data'].get('dt1', 0.0), step=None, format='%e')
                st.session_state['params_data']['dt2'] = st.number_input('dt2', min_value=None, max_value=None, value=st.session_state['params_data'].get('dt2', 0.0), step=None, format='%e')
                st.session_state['params_data']['clock_offset_std'] = st.number_input('Clock Offset Noise Standard Deviation', min_value=0.0, value=st.session_state['params_data'].get('clock_offset_std', 0.0), step=None, format='%e')
                st.subheader('Position')
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state['params_data']['ground_station_latitude'] = st.number_input('Latitude of ground station (degrees)', min_value=-90.0, max_value=90.0, value=st.session_state['params_data'].get('ground_station_latitude', 0.0), step=0.01)
                with col2:
                    st.session_state['params_data']['ground_station_longitude'] = st.number_input('Longitude of ground station (degrees)', min_value=-180.0, max_value=180.0, value=st.session_state['params_data'].get('ground_station_longitude', 0.0), step=0.01)
                col1, col2 = st.columns(2)
                with col1:
                    st.session_state['params_data']['ground_station_altitude'] = st.number_input('Altitude of ground station (meters)', min_value=0.0, value=st.session_state['params_data'].get('ground_station_altitude', 0.0), step=1.0)
                with col2:
                    st.session_state['params_data']['minimum_elevation_angle'] = st.number_input('Minimum Elevation Angle (degrees)', min_value=0.0, max_value=90.0, value=st.session_state['params_data'].get('minimum_elevation_angle', 0.0), step=1.0)

            with st.expander('Other Simulation Parameters', expanded=st.session_state.get('expand_other_params', True)):
                st.session_state['params_data']['epochs'] = st.number_input('Simulation Duration (seconds)', min_value=1, value=st.session_state['params_data'].get('epochs', 1), step=1)
                st.session_state['params_data']['GMe'] = st.number_input('Earth\'s Standard Gravitational Parameter', min_value=None, max_value=None, value=st.session_state['params_data'].get('GMe', 0.0), step=None, format='%e')
                st.session_state['params_data']['OmegaEdot'] = st.number_input('Earth\'s Angular Velocity', min_value=None, max_value=None, value=st.session_state['params_data'].get('OmegaEdot', 0.0), step=None, format='%e')

            with st.expander('Ionospheric Model Parameters (Klobuchar)', expanded=st.session_state.get('expand_klobuchar_params', True)):
                st.session_state['params_data']['alpha0'] = st.number_input('Alpha0', min_value=None, max_value=None, value=st.session_state['params_data'].get('alpha0', 0.0), step=None, format='%e')
                st.session_state['params_data']['alpha1'] = st.number_input('Alpha1', min_value=None, max_value=None, value=st.session_state['params_data'].get('alpha1', 0.0), step=None, format='%e')
                st.session_state['params_data']['alpha2'] = st.number_input('Alpha2', min_value=None, max_value=None, value=st.session_state['params_data'].get('alpha2', 0.0), step=None, format='%e')
                st.session_state['params_data']['alpha3'] = st.number_input('Alpha3', min_value=None, max_value=None, value=st.session_state['params_data'].get('alpha3', 0.0), step=None, format='%e')
                st.session_state['params_data']['beta0'] = st.number_input('Beta0', min_value=None, max_value=None, value=st.session_state['params_data'].get('beta0', 0.0), step=None, format='%e')
                st.session_state['params_data']['beta1'] = st.number_input('Beta1', min_value=None, max_value=None, value=st.session_state['params_data'].get('beta1', 0.0), step=None, format='%e')
                st.session_state['params_data']['beta2'] = st.number_input('Beta2', min_value=None, max_value=None, value=st.session_state['params_data'].get('beta2', 0.0), step=None, format='%e')
                st.session_state['params_data']['beta3'] = st.number_input('Beta3', min_value=None, max_value=None, value=st.session_state['params_data'].get('beta3', 0.0), step=None, format='%e')

            with st.expander('Cycle Slip Parameters', expanded=st.session_state.get('expand_cycle_slip_params', True)):
                st.session_state['params_data']['cycle_slip_epoch'] = st.number_input('epoch of cycle slip', min_value=1, max_value=st.session_state['params_data'].get('epochs', 1)-1, value=st.session_state['params_data'].get('cycle_slip_epoch', 1), step=1)

        else:
            st.error('An unexpected error occurred. Please refresh the page and try again.')