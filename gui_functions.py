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
    if st.button('Compute observations', width='stretch'):
        with st.spinner(text="The computation has started. Please wait...", show_time=True):
            try:
                L1, L2 = run_simulation()
                st.session_state['computation_done'] = True
            except Exception as e:
                st.error(f'An error occurred during computation: {e}')
                return
        st.success('Computation completed! Click below to download the output files.')

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
        
        l1_and_l2 = plot_L1_L2(L1, L2)
        plot_diff1, diff1 = plot_differences(L1, 'Differences in L1 Observations', 'blue')
        plot_diff2, diff2 = plot_differences(L2, 'Differences in L2 Observations', 'orange')
        plot_diff, _ = plot_diff_of_diff(diff1, diff2)
        _lock = RLock()

        with _lock:
            st.pyplot(l1_and_l2)
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(plot_diff1)
            with col2:
                st.pyplot(plot_diff2)

            st.pyplot(plot_diff)

