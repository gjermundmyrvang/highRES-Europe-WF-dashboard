import streamlit as st
from .render_system_metrics import render_system_metrics


def render_overview(df, hour_data, scenario_name):
    st.title("Scenario Overview")
    st.caption(scenario_name)
    return render_system_metrics(df, hour_data)
