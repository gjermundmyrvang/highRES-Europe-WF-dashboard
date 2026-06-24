import streamlit as st
from .render_system_metrics import render_system_metrics

def render_overview(df):
    st.title("System Overview")
    render_system_metrics(df)