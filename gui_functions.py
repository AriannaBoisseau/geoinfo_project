import json
import streamlit as st
import pandas as pd

from main_functionalities import run_simulation

def show_map(lat, lon):
    st.subheader('Ground Station Location')
    data = {
        'lat': [lat],
        'lon': [lon],
    }
    df = pd.DataFrame(data)
    st.map(df)

def show_computation_button():
    if st.button('Compute observations'):
        st.info('The computation has started. Please wait...')
        run_simulation()
        st.success('Computation completed! Click below to download the output files.')

        with open('output/L1_observations.csv', 'rb') as f1, open('output/L2_observations.csv', 'rb') as f2:
            st.download_button(
                label='Download L1 Observations',
                data=f1,
                file_name='L1_observations.csv',
                mime='text/csv'
            )
            st.download_button(
                label='Download L2 Observations',
                data=f2,
                file_name='L2_observations.csv',
                mime='text/csv'
            )