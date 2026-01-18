import json
import streamlit as st
import pandas as pd
import numpy as np
from threading import RLock

from main_functionalities import run_simulation
from plots import plot_L1_L2, plot_differences, plot_diff_of_diff
from functions import compute_wavelength, cycle_slip_generator, identify_cycle_slip

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

        run_add_cycle_slip()
        if st.session_state.get('cycle_slip_added'):
            st.session_state.cycle_slip_added = False

def run_add_cycle_slip():

    # Unified params source
    params = st.session_state.get('params_data')
    if params is None:
        st.error("Parameters are missing. Please provide parameters first.")
        return

    # Ensure observations exist
    L1 = st.session_state.get('L1_observations')
    L2 = st.session_state.get('L2_observations')
    if L1 is None or L2 is None:
        st.error("Observations not available. Run the computation first.")
        return

    # Pull needed params with sane defaults
    cycle_slip_epoch = int(params.get('cycle_slip_epoch', 1))
    fundamental_frequency = params.get('fundamental_frequency')
    freq_mult_L1 = params.get('frequency_multiplier_L1')
    freq_mult_L2 = params.get('frequency_multiplier_L2')

    if fundamental_frequency is None or freq_mult_L1 is None or freq_mult_L2 is None:
        st.error("Frequency parameters are missing. Please provide them.")
        return

    col1, col2, _ = st.columns([1,3,1])
    with col1:
        st.image('images/favicon.png', width=100)
    with col2:
        st.title('Cycle slip simulation')

    epoch = np.array([cycle_slip_epoch], dtype=int)

    w1 = compute_wavelength(fundamental_frequency, freq_mult_L1)
    w2 = compute_wavelength(fundamental_frequency, freq_mult_L2)

    L1_dirty = cycle_slip_generator(w1, L1, epoch)
    L2_dirty = cycle_slip_generator(w2, L2, epoch)

    st.session_state['cycle_slip_added'] = True

    l1_and_l2 = plot_L1_L2(L1_dirty, L2_dirty)
    plot_diff1, diff1 = plot_differences(L1_dirty, 'blue')
    plot_diff2, diff2 = plot_differences(L2_dirty, 'orange')
    plot_diff, diff_of_diff = plot_diff_of_diff(diff1, diff2)
    st.session_state['diff_of_diff'] = diff_of_diff
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

def show_cycle_slip_section():
    # Render only when diff_of_diff exists
    diff_of_diff = st.session_state.get('diff_of_diff')
    if diff_of_diff is None:
        return

    col1, col2, _ = st.columns([1,3,1])
    with col1:
        st.image('images/favicon.png', width=100)
    with col2:
        st.title('Cycle slip identification')

    cycle_splip_detected_epoch = identify_cycle_slip(diff_of_diff)
    st.success(f'Cycle slip detected at epoch: {cycle_splip_detected_epoch}')