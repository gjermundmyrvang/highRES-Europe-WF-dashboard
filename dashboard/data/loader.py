import streamlit as st
from data.capacity import capacity_summary
from data.cost_transformer import (
    generate_cost_breakdown,
    get_total_costs_raw,
)
from data_loader import clean_results, load_results, load_sets, table
from pathlib import Path


@st.cache_data
def load_scenario(path, gams_path, variables):
    return clean_results(load_results(Path(path), Path(gams_path), variables))


@st.cache_data
def load_sets_cached(path, gams_path, sets):
    return load_sets(Path(path), Path(gams_path), sets)


@st.cache_data
def load_scenario_summary(
    gdx_path, gams_path, variables, user_sets, inflation_factor, rate
):
    data = load_scenario(gdx_path, gams_path, variables)
    sets = load_sets(gdx_path, gams_path, user_sets)
    gbp_value, adjusted_cost = get_total_costs_raw(data, inflation_factor, rate)
    cap = capacity_summary(data, sets, adjusted_cost)

    vre_techs = list(table(sets, "vre")["g"])

    # Tech breakdown for VRE comparison
    tech_breakdown = data["var_new_pcap"].groupby("g")["value"].sum()

    # Cost breakdown, total values per category (e.g generation costs)
    cost_dict = generate_cost_breakdown(data, inflation_factor, rate)
    # Hide column with the category total cost in gbp (not relevant here)
    cost_dict_filtered = {k: v for k, v in cost_dict.items() if "_gbp" not in k}

    # Storage breakdown
    storage_df = data["var_tot_store_pcap"].groupby("s")["value"].sum()

    return {
        "total_installed": cap["total_installed"],
        "new_installed": cap["new_installed"],
        "total_vre": cap["total_vre"],
        "new_vre": cap["new_vre"],
        "tot_storage": cap["tot_storage"],
        "by_demand": cap["by_demand"],
        "cost_raw": adjusted_cost,
        "gbp_value": gbp_value,
        "tech_breakdown": tech_breakdown,
        "vre_techs": vre_techs,
        "cost_breakdown": cost_dict_filtered,
        "storage_breakdown": storage_df,
    }
