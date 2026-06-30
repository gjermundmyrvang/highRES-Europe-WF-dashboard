import streamlit as st
import json
from data_loader import find_work_folders, load_sets
from data.loader import load_scenario
from ui import render_sidebar
from ui.tabs import render_overview, render_capacity
from pathlib import Path

# ---------- PAGE SETUP ------------
st.set_page_config(layout="wide")
st.title("highRES Dashboard")
st.markdown("""
    > The model is used to plan least-cost electricity systems for Europe and specifically designed to analyse the effects of high shares of variable renewables and explore integration/flexibility options. It does this by comparing and trading off potential options to integrate renewables into the system including the extension of the transmission grid, interconnection with other countries, building flexible generation (e.g. gas power stations), renewable curtailment and energy storage.
            """)


def main():
    if "added_scenarios" not in st.session_state:
        st.session_state.added_scenarios = {}

    scenario_gdx = render_sidebar(find_work_folders("./"))  # Load focused scenario

    data = load_scenario(scenario_gdx)
    sets = load_sets(scenario_gdx)

    with open("intermediate_data/region/shapes/europe_onshore.geojson") as f:
        geo = json.load(f)

    tab1, tab2, tab3 = st.tabs(["Overview", "Explore Capacity", "README"])

    with tab1:
        render_overview(data, sets)

    with tab2:
        render_capacity(data, sets, geo)

    with tab3:
        left_pad, center_content, right_pad = st.columns([1, 2, 1])
        with center_content:
            _render_readme()


def _render_readme():
    file = Path("./dashboard/README.md").read_text(encoding="utf-8")
    st.markdown(file, unsafe_allow_html=True, width=800)


if __name__ == "__main__":
    main()
