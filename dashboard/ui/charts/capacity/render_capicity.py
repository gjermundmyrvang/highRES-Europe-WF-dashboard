import streamlit as st
import numpy as np
from .dimension_one import render_dimension_one
from .dimension_two import render_dimension_two
from .dimension_three import render_dimension_three

def render_capacity_charts(data, geo):
    st.title("Capacity & Potential Exploration")
    st.markdown("""
    > This tab explores installed capacity from three angles. Dimension 1 looks at what has been built across countries and technologies. Dimension 2 compares installed capacity against the available VRE potential to show how much is being utilized. Dimension 3 translates this into land area, giving a spatial perspective on how much ground is being used versus what is available
                """)
 
    tot_z = data["var_tot_pcap_z"]
    potential_z = data["area"].replace([np.inf, -np.inf], np.nan)  # HydroRoR is INF+
 
    render_dimension_one(tot_z)
    st.divider()
    render_dimension_two(tot_z, potential_z)
    st.divider()
    render_dimension_three(tot_z, potential_z, geo)