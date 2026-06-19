import streamlit as st
import numpy as np
from .dimension_one import render_dimension_one
from .dimension_two import render_dimension_two

def render_capacity_charts(data):
    st.title("Installed Capacity Exploration")
 
    tot_z = data["var_tot_pcap_z"]
    potential_z = data["area"].replace([np.inf, -np.inf], np.nan)  # HydroRoR is INF+
 
    render_dimension_one(tot_z)
    render_dimension_two(tot_z, potential_z)