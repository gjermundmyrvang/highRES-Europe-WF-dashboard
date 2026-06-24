import streamlit as st
import json
from data_loader import find_work_folders, load_sets 
from data.loader import load_scenario
from ui import render_sidebar
from ui.tabs import render_overview, render_capacity


# ---------- PAGE SETUP ------------
st.set_page_config(layout="wide")
st.title("highRES Dashboard")
st.caption("Energy system model results (page under development...)")

def main():
    scenario = render_sidebar(find_work_folders("./")) # Load focused scenario

    data = load_scenario(scenario / "results.gdx")
    hour_data = load_sets(scenario / "results.gdx")

    with open("intermediate_data/region/shapes/europe_onshore.geojson") as f:
        geo = json.load(f)

    tab1, tab2, tab3 = st.tabs(["Overview", "Explore Capacity", "Map"])

    with tab1:
        render_overview(data, hour_data)

    with tab2:
        render_capacity(data, geo)

    with tab3:
        st.title("Tab 3: TODO")
    
if __name__ == "__main__":
    main()