import streamlit as st
import json
from data_loader import find_work_folders 
from data.loader import load_scenario
from ui.sidebar import render_sidebar
from ui.charts.total_capacity import render_total_capicity
from ui.charts.zone_capacity_v2 import render_zone_capicity_v2
from ui.charts.zone_capacity import render_zone_capicity

# ---------- PAGE SETUP ------------
st.set_page_config(layout="wide")
st.title("highRES Dashboard")
st.caption("Energy system model results (page under development...)")

def main():
    scenario = render_sidebar(find_work_folders("./")) # Load focused scenario

    data = load_scenario(scenario / "results.gdx")

    total_cost = data["costs"].iloc[0]["value"]
    st.subheader(f"Total Cost: {round(total_cost, 3)}")


    # --------------- CHARTS (Aggregated for all countries) ---------
    render_total_capicity(data)
    st.divider()
        
    # -------------- Zone Map ------------------
    with open("intermediate_data/region/shapes/europe_onshore.geojson") as f:
        geo = json.load(f)
    render_zone_capicity(data, geo)
    st.divider()

    # -------------- Installed vs. Potential ------------------
    render_zone_capicity_v2(data)
    st.divider()
    
if __name__ == "__main__":
    main()