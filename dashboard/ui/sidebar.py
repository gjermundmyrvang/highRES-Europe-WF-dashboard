import streamlit as st

def render_sidebar(scenario_paths):
    with st.sidebar:
        st.header("Settings")
        selected = st.selectbox("Scenario", options=list(scenario_paths.keys()))
        return selected