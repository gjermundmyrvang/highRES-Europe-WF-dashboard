import streamlit as st
import pandas as pd
from data.loader import load_scenario
from data.capacity import capacity_summary


def render_scenarios(all_scenarios: dict):
    st.title("Scenarios Overview")

    selected = st.multiselect(
        "Select scenarios to compare",
        options=list(all_scenarios.keys()),
        default=list(all_scenarios.keys()),
    )

    visible = {name: path for name, path in all_scenarios.items() if name in selected}

    rows = []
    for scenario_name, gdx_path in visible.items():
        try:
            data = load_scenario(gdx_path)
            cap = capacity_summary(data)
            rows.append(
                {
                    "Scenario": scenario_name,
                    "Total Capacity (GW)": cap["total_installed"],
                    "New Capacity (GW)": cap["new_installed"],
                    "Total VRE (GW)": cap["total_vre"],
                    "New VRE (GW)": cap["new_vre"],
                }
            )
        except Exception as e:
            rows.append(
                {
                    "Scenario": scenario_name,
                    "Total Capacity (GW)": "error",
                    "New Capacity (GW)": "error",
                    "Total VRE (GW)": "error",
                    "New VRE (GW)": "error",
                }
            )

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True)
