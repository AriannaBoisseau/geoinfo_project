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
    st.title('Orbit simulation')

# sidebar
render_sidebar()

_, col2, _ = st.columns([1,3,1])
with col2:
    params = st.session_state.get('params_data')
    if not params:
        st.info('Please provide the parameters using the sidebar to the left.')
    else:
        lat = params.get('ground_station_latitude')
        lon = params.get('ground_station_longitude')
        if lat is None or lon is None:
            st.info('Please provide the ground station parameters using the sidebar to the left.')
        else:
            show_map(lat, lon)
            show_computation_button()

# if st.session_state.computation_done == True:
#     if st.session_state.get('cycle_slip_added') is None:
#         col1, col2, _ = st.columns([1,3,1])
#         with col1:
#             st.image('images/favicon.png', width=100)
#         with col2:
#             st.title('Cycle slip simulation')
#             st.caption('In this section you can provide parameters to cycle slips to the simulated GNSS data.')
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 st.number_input('epoch of cycle slip', min_value=0, max_value=st.session_state.epochs-1, value=0, step=1, key='cycle_slip_epoch')
#             with col2:
#                 st.number_input('number of cycles to add on L1', min_value=1, max_value=None, value=1, step=1, key='cycle_slip_L1')
#             with col3:
#                 st.number_input('number of cycles to add on L2', min_value=1, max_value=None, value=1, step=1, key='cycle_slip_L2')
                
#             st.button('Add Cycle Slip', key='add_cycle_slip_button', use_container_width=True, on_click=run_add_cycle_slip)

#     if st.session_state.get('cycle_slip_added'):
#         st.success('Cycle slip added successfully!')
#         st.session_state.cycle_slip_added = False