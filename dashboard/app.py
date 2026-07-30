from pathlib import Path

import streamlit as st
from data_loader import (
    load_scenarios,
    load_sets,
    load_config,
    check_user_config,
)
from data.loader import load_scenario
from ui import render_sidebar
from ui.tabs import (
    render_overview,
    render_capacity,
    render_scenarios,
    render_utilization,
    render_map,
)
from data.transformer import load_country_areas
import json

# ---------- PAGE SETUP ------------
st.markdown(
    """
<style>
div[role="radiogroup"] label {
    font-size: 20px;
}
div[role="radiogroup"] label > div:first-child {
    width: 24px;
    height: 24px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
[data-testid="stBottom"] > div {
    background-color: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    margin-top: 4rem;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    @media (max-width: 1300px) {
        /* Change the font size of the metric value */
        [data-testid="stMetricValue"] {
            font-size: 18px;
        }
        
        /* Change the font size of the metric label */
        [data-testid="stMetricLabel"] p {
            font-size: 14px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.set_page_config(layout="wide")

st.header("highRES Dashboard")
st.page_link(
    "pages/1_README.py",
    label="How to use this dashboard",
    icon=":material/library_books:",
)
st.markdown("""
    > The model is used to plan least-cost electricity systems for Europe and specifically designed to analyse the effects of high shares of variable renewables and explore integration/flexibility options. It does this by comparing and trading off potential options to integrate renewables into the system including the extension of the transmission grid, interconnection with other countries, building flexible generation (e.g. gas power stations), renewable curtailment and energy storage.
            """)


def main():
    if "added_scenarios" not in st.session_state:
        st.session_state.added_scenarios = {}

    # Sidebar
    render_sidebar()

    config = load_config()

    # FIRSTLY CHECK IF CONFIG IS SET UP CORRECTLY
    is_valid, errors = check_user_config(config)

    if not is_valid:
        st.error(
            "Make sure **`dashboard/dashboard_config.yaml`** points to valid folders",
            title="Configuration is invalid.",
            icon=":material/error:",
        )
        for error in errors:
            st.warning(error)
        st.stop()

    loaded = {}
    results_path = config.get("results_path")

    # Small check if to display warning about using example data
    if results_path == "dashboard/example_scenarios":
        st.warning(
            title=":material/warning: Dashboard running on example data",
            body="The data presented may therefore look a bit weird or not correct. The example data is just to demonstrate the overall layout and functionality.",
        )

    if results_path and Path(results_path).exists():
        try:
            loaded = load_scenarios(results_path)
        except FileNotFoundError:
            # Not stopping yet! The user might want to add runtime-added scenarios.
            pass

    all_scenarios = {**loaded, **st.session_state.added_scenarios}

    if not all_scenarios:
        st.error(
            "**No scenarios available**",
            icon=":material/folder_open:",
        )
        if results_path:
            st.info(
                f"No `.gdx` files found in `{results_path}` and no scenarios uploaded. "
                "Please upload a scenario via the sidebar or check your results folder structure."
            )
        else:
            st.info(
                "No `results_path` configured in `dashboard_config.yaml`. "
                "Please add a folder with `.gdx` scenarios using the sidebar to continue."
            )
        st.stop()

    # Sticky bottom with buttons for switching scenarios
    if "current_scenario" not in st.session_state:  # For feedback purpose
        st.session_state.current_scenario = list(all_scenarios.keys())[0]
    with st.bottom:
        radio, display = st.columns([0.1, 0.9])
        with radio:
            layout = st.radio("Layout", ["Dropdown", "All"], horizontal=True)
        with display:
            if layout == "Dropdown":
                selected = st.selectbox(
                    "**Active scenario**",
                    options=list(all_scenarios.keys()),
                )
            else:
                selected = st.segmented_control(
                    "**Active scenario**",
                    options=list(all_scenarios.keys()),
                    default=list(all_scenarios.keys())[0],
                )
    if selected and selected != st.session_state.current_scenario:
        st.session_state.current_scenario = selected
        st.toast(
            f"Switched to **{selected}**",
            icon=":material/check_circle:",
            duration="short",
        )

    scenario_gdx = all_scenarios[selected]

    # GET CONFIG DATA
    gams_path = config.get("gams_path")
    geo_path = config.get("geojson_path")
    variables = config.get("variables")
    user_sets = config.get("sets")

    # LOAD DATA
    with st.spinner("Loading tables from gdx file"):
        data = load_scenario(scenario_gdx, gams_path, variables)
        sets = load_sets(scenario_gdx, gams_path, user_sets)

    # Create dict of country areas in km2
    country_areas = load_country_areas(geo_path)

    # Geo
    with open(geo_path) as f:
        geo = json.load(f)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Map", "Explore Capacity", "VRE Deployment", "Scenarios"]
    )

    with tab1:
        inflation_factor, selected_currency, rate, gbp_value = render_overview(
            data, sets
        )

    with tab2:
        render_map(data, geo, inflation_factor, selected_currency, rate, gbp_value)

    with tab3:
        render_capacity(data, sets)

    with tab4:
        render_utilization(data, country_areas)

    with tab5:
        render_scenarios(
            all_scenarios, config, inflation_factor, selected_currency, rate
        )


if __name__ == "__main__":
    main()
