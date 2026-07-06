import streamlit as st
from data.capacity import capacity_summary


def render_key_data(df):
    df = capacity_summary(df)

    total_installed = df["total_installed"]
    total_vre = df["total_vre"]
    new_installed = df["new_installed"]
    new_vre = df["new_vre"]

    col1, col2, col3, col4 = st.columns(4, border=True, gap="large")

    col1.metric(":material/bolt: Total Installed", f"{total_installed} GW")
    col2.metric(":material/eco: of which VRE", f"{total_vre} GW")
    col3.metric(":material/construction: Newly Built", f"{new_installed} GW")
    col4.metric(":material/eco: of which VRE", f"{new_vre} GW")
