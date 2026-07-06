import streamlit as st
from data_loader import clean_results, load_results, load_sets
from pathlib import Path


@st.cache_data
def load_scenario(path):
    return clean_results(load_results(Path(path)))


@st.cache_data
def load_sets_cached(path):
    return load_sets(Path(path))
