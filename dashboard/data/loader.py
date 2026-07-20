import streamlit as st
from data_loader import clean_results, load_results, load_sets
from pathlib import Path


@st.cache_data
def load_scenario(path, gams_path):
    return clean_results(load_results(Path(path), Path(gams_path)))


@st.cache_data
def load_sets_cached(path, gams_path):
    return load_sets(Path(path), Path(gams_path))
