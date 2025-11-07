import json
import streamlit as st
import pandas as pd

def show_map(lat, lon):
    st.subheader('Ground Station Location')
    data = {
        'lat': [lat],
        'lon': [lon],
    }
    df = pd.DataFrame(data)
    st.map(df)