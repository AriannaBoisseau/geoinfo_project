import json
import streamlit as st
import pandas as pd
from threading import RLock

from main_functionalities import run_simulation
from plots import plot_L1_L2, plot_differences, plot_diff_of_diff

def show_map(lat, lon):
    st.subheader('Ground Station Location')
    data = {
        'lat': [lat],
        'lon': [lon],
    }
    df = pd.DataFrame(data)
    st.map(df)

def show_computation_button():
    if st.session_state.get('computation_running') == False and st.session_state.get('computation_done') == False:
        if st.button('Compute observations', key='compute_button', use_container_width=True):
            st.session_state['computation_running'] = True
            st.rerun()

    if st.session_state.get('computation_running') == True:
        with st.spinner(text="The computation has started. Please wait...", show_time=True):
            try:
                L1, L2 = run_simulation()
                st.session_state['L1_observations'] = L1
                st.session_state['L2_observations'] = L2
                st.session_state['computation_running'] = False
                st.session_state['computation_done'] = True
            except Exception as e:
                st.error(f'An error occurred during computation: {e}')
                st.session_state['computation_running'] = False
                return


    if st.session_state.get('computation_done') == True:
        st.success('Computation completed successfully!')
        L1 = st.session_state['L1_observations']
        L2 = st.session_state['L2_observations']

        col1, col2 = st.columns(2)
        with col1:
            st.metric('L1 Observations Generated', f"{len(L1)} epochs")
        with col2:
            st.metric('L2 Observations Generated', f"{len(L2)} epochs")
        
        l1_and_l2 = plot_L1_L2(L1, L2)
        plot_diff1, diff1 = plot_differences(L1, 'blue')
        plot_diff2, diff2 = plot_differences(L2, 'orange')
        plot_diff, _ = plot_diff_of_diff(diff1, diff2)
        _lock = RLock()

        with _lock:
            st.subheader('L1 and L2 Observations')
            st.pyplot(l1_and_l2)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader('Differences in L1 Observations')
                st.pyplot(plot_diff1)
            with col2:
                st.subheader('Differences in L2 Observations')
                st.pyplot(plot_diff2)

            st.subheader('Difference of Differences between L1 and L2 Observations')
            st.pyplot(plot_diff)

        with open('output/L1_observations.csv', 'rb') as f1, open('output/L2_observations.csv', 'rb') as f2:
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label='Download L1 Observations',
                    data=f1,
                    file_name='L1_observations.csv',
                    mime='text/csv'
                )
            with col2:
                st.download_button(
                    label='Download L2 Observations',
                    data=f2,
                    file_name='L2_observations.csv',
                    mime='text/csv'
                )