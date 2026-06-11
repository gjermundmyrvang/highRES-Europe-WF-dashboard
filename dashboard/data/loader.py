import streamlit as st
from data_loader import clean_results, load_results 

@st.cache_data
def load_scenario(path):
    return clean_results(load_results(path))