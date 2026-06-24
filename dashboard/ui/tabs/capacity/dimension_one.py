import streamlit as st
from .figures import render_capacity_pies
from ui.components import filter_countries
 
def render_dimension_one(tot_z):
    st.subheader("Dimension 1: Explore whats been installed by countries?")
    st.text("Dataset: var_tot_pcap_z")
 
    col1, col2 = st.columns([3, 1])
    with col1:
        filtered = filter_countries(tot_z)
    with col2:
        cols = st.slider("Columns", min_value=2, max_value=6, value=3)
 
    fig = render_capacity_pies(filtered, cols=cols)
    st.plotly_chart(fig)
 
    with st.expander("See data table"):
        st.dataframe(filtered)