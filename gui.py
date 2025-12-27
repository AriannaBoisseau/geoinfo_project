import streamlit as st

from gui_functions import *
from sidebar import render_sidebar

st.set_page_config(page_title='Cycle Slip Simulation and Identification', page_icon='images/favicon.png', layout="wide")
st.session_state.setdefault('computation_done', False)
st.session_state.setdefault('computation_running', False)

col1, col2, _ = st.columns([1,3,1])
with col1:
    st.image('images/favicon.png', width=100)
with col2:
    st.title('Cycle slip simulation')

# sidebar
render_sidebar()

_, col2, _ = st.columns([1,3,1])
with col2:
    if 'ground_station_latitude' not in st.session_state or 'ground_station_longitude' not in st.session_state:
        st.info('Please provide the ground station parameters using the sidebar to the left.')
    else:
        show_map(st.session_state.ground_station_latitude, st.session_state.ground_station_longitude)
        show_computation_button()

if st.session_state.computation_done == True:
    col1, col2, _ = st.columns([1,3,1])
    with col1:
        st.image('images/favicon.png', width=100)
    with col2:
        st.title('Cycle slip identification')