import streamlit as st

def render_sidebar(work_folders: dict):
    with st.sidebar:
        st.header("Settings")

        selected_folder = st.selectbox(
            "Folder",
            options=list(work_folders.keys()),
        )

        scenarios = work_folders[selected_folder]
        selected_scenario = st.selectbox(
            "Scenario",
            options=list(scenarios.keys()),
        )

        return scenarios[selected_scenario]