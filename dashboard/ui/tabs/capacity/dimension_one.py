import streamlit as st
from .figures import render_capacity_pies
from ui.components import filter_countries
 
def render_dimension_one(tot_z, new_z):
    st.subheader("Dimension 1: Explore whats been installed by countries?")
    st.markdown("Dataset: `var_tot_pcap_z` or `var_new_pcap_z`")

    selected_table = st.radio(
        "Select focused table",
        ["`var_tot_pcap_z`", "`var_new_pcap_z`"]
    )

    focused = tot_z if selected_table == "var_tot_pcap_z" else new_z
 
    col1, col2 = st.columns([3, 1])
    with col1:
        filtered = filter_countries(focused)
    with col2:
        cols = st.slider("Columns", min_value=2, max_value=6, value=3)
 
    fig = render_capacity_pies(filtered, cols=cols)
    st.plotly_chart(fig)
 
    with st.expander("See data table"):
        st.dataframe(filtered)