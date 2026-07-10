import streamlit as st
from data_loader import (
    load_sets,
    load_config,
    load_standard_scenarios,
)
from data.loader import load_scenario
from ui import render_sidebar
from ui.tabs import render_overview, render_capacity, render_scenarios

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

st.set_page_config(layout="wide")
st.title("highRES Dashboard")
st.page_link(
    "pages/1_README.py",
    label=":material/library_books: &nbsp; How to use this dashboard",
)
st.markdown("""
    > The model is used to plan least-cost electricity systems for Europe and specifically designed to analyse the effects of high shares of variable renewables and explore integration/flexibility options. It does this by comparing and trading off potential options to integrate renewables into the system including the extension of the transmission grid, interconnection with other countries, building flexible generation (e.g. gas power stations), renewable curtailment and energy storage.
            """)


def main():
    if "added_scenarios" not in st.session_state:
        st.session_state.added_scenarios = {}

    config = load_config()

    # Load standard scenarios from config path
    standard = load_standard_scenarios(config["results_path"])

    # Merge with any user-added custom scenarios
    all_scenarios = {**standard, **st.session_state.added_scenarios}

    # Sidebar with scenario settings
    render_sidebar()

    # Sticky bottom with buttons for switching scenarios
    with st.bottom:
        selected = st.segmented_control(
            "**Active scenario**",
            options=list(all_scenarios.keys()),
            default=list(all_scenarios.keys())[0],
        )

    scenario_gdx = all_scenarios[selected]

    data = load_scenario(scenario_gdx)
    sets = load_sets(scenario_gdx)

    tab1, tab2, tab3 = st.tabs(["Overview", "Explore Capacity", "Scenarios"])

    with tab1:
        render_overview(data, sets, scenario_gdx)

    with tab2:
        render_capacity(data, sets)

    with tab3:
        render_scenarios(all_scenarios)


if __name__ == "__main__":
    main()
