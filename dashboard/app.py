import streamlit as st
import json
from data_loader import find_work_folders 
from data.loader import load_scenario
from ui import render_sidebar, render_system_metrics
from ui.charts import render_total_capicity, render_zone_capicity, render_zone_capicity_v2, render_capacity_charts


# ---------- PAGE SETUP ------------
st.set_page_config(layout="wide")
st.title("highRES Dashboard")
st.caption("Energy system model results (page under development...)")

def main():
    scenario = render_sidebar(find_work_folders("./")) # Load focused scenario

    data = load_scenario(scenario / "results.gdx")

    tab1, tab2 = st.tabs(["Overview", "Explore Capacity"])

    with tab1:
        render_system_metrics(data)

        # --------------- CHARTS (Aggregated for all countries) ---------
        render_total_capicity(data)
        st.divider()
            
        # -------------- Zone Map ------------------
        with open("intermediate_data/region/shapes/europe_onshore.geojson") as f:
            geo = json.load(f)
        render_zone_capicity(data, geo)
        st.divider()

        # -------------- Installed vs. Potential ------------------
        # render_zone_capicity_v2(data)
        # st.divider()

    with tab2:

        # ------------ EXPLORATION OF CAPACITY CHARTS -------------------
        render_capacity_charts(data)
    
if __name__ == "__main__":
    main()