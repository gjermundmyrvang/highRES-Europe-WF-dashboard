import streamlit as st
import json
from pathlib import Path
from data_loader import find_result_files 
from data.loader import load_scenario
from ui.sidebar import render_sidebar
from ui.charts.total_capacity import render_total_capicity
from ui.charts.zone_capacity import render_zone_capicity
import argparse

TECH_COLORS = {
    "Solar":               "#F5C518",
    "Windonshore":         "#4A90D9",
    "Windoffshore":        "#1B5FA8",
    "WindoffshoreFloat":   "#0D3B6E",
    "HydroRoR":            "#2ECC71",
    "HydroRes":            "#1A8C4E",
    "NuclearEPR":          "#E74C3C",
}

parser = argparse.ArgumentParser()
parser.add_argument("--results-path", type=str, default=None)
args = parser.parse_args()

if args.results_path:
    scenario_paths = {Path(args.results_path).name: Path(args.results_path) / "results.gdx"}
else:
    scenario_paths = find_result_files()


# ---------- PAGE SETUP ------------
st.set_page_config(layout="wide")
st.title("highRES Dashboard")
st.caption("Energy system model results (page under development...)")

def main():
    scenario = render_sidebar(scenario_paths)

    data = load_scenario(scenario_paths[scenario])

    col1, col2 = st.columns(2)

    # --------------- CHARTS (Aggregated for all countries) ---------
    with col1:
        render_total_capicity(data)
        
    # -------------- CHARTS (By zones) ------------------
    with open("intermediate_data/region/shapes/europe_onshore.geojson") as f:
        geo = json.load(f)

    with col2:
        render_zone_capicity(data, geo)
    
if __name__ == "__main__":
    main()