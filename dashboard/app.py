import streamlit as st
import json
from data_loader import find_work_folders, load_sets, load_config
from data.loader import load_scenario
from ui import render_sidebar
from ui.tabs import render_overview, render_capacity

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
    scenario_gdx = render_sidebar(find_work_folders(config["results_path"]))

    data = load_scenario(scenario_gdx)
    sets = load_sets(scenario_gdx)

    tab1, tab2 = st.tabs(["Overview", "Explore Capacity"])

    with tab1:
        render_overview(data, sets)

    with tab2:
        render_capacity(data, sets)


if __name__ == "__main__":
    main()
