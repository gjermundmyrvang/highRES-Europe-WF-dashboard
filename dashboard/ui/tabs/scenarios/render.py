import streamlit as st
import pandas as pd
from data.loader import load_scenario, load_sets
from data.capacity import capacity_summary
from data.cost_transformer import (
    adjust_currency,
    adjust_inflation,
    get_exchange_rate,
    format_money,
)


def render_scenarios(
    all_scenarios: dict, config, inflation_factor, selected_currency, rate
):
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
            data = load_scenario(gdx_path, config["gams_path"])
            sets = load_sets(gdx_path, config["gams_path"])
            cap = capacity_summary(data, sets)

            # Total Cost
            total_cost = data["costs"].iloc[0]["value"]
            gbp_value = total_cost * 1_000_000
            adjusted_gbp = adjust_inflation(gbp_value, inflation_factor)
            adjusted = format_money(adjust_currency(adjusted_gbp, rate))

            rows.append(
                {
                    "Scenario": scenario_name,
                    "Total Capacity (GW)": cap["total_installed"],
                    "New Capacity (GW)": cap["new_installed"],
                    "Total VRE (GW)": cap["total_vre"],
                    "New VRE (GW)": cap["new_vre"],
                    f"Total Cost ({selected_currency['iso_code']})": f"{adjusted}",
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
                    "Total Cost": "error",
                }
            )

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True)
