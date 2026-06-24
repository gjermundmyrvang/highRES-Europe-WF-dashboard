import streamlit as st
from .render_system_metrics import render_system_metrics

def render_overview(df, hour_data):
    st.title("System Overview")
    render_system_metrics(df, hour_data)