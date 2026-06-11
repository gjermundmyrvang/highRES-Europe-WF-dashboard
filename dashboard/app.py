import streamlit as st
import plotly.express as px
import json
from data_loader import find_result_files, clean_results, load_results 

TECH_COLORS = {
    "Solar":               "#F5C518",
    "Windonshore":         "#4A90D9",
    "Windoffshore":        "#1B5FA8",
    "WindoffshoreFloat":   "#0D3B6E",
    "HydroRoR":            "#2ECC71",
    "HydroRes":            "#1A8C4E",
    "NuclearEPR":          "#E74C3C",
}

st.set_page_config(layout="wide")
st.title("highRES Dashboard")
st.caption("Energy system model results")

scenario_paths = find_result_files()

# ---------- SIDEBAR SCENARIO SELECTOR ------------
with st.sidebar:
    st.header("Settings")
    selected = st.selectbox("Scenario", options=list(scenario_paths.keys()))

@st.cache_data
def get_data(scenario):
    return clean_results(load_results(scenario_paths[scenario]))

data = get_data(selected) # Data is cached to avoid unneccessary reloads

col1, col2 = st.columns(2)

# --------------------- CHARTS (Aggregated for all countries) ------------------
with col1:
    tot = data["var_tot_pcap"].copy()
    new = data["var_new_pcap"].copy()

    combined = tot.merge(new, on="g", how="left", suffixes=("_tot", "_new"))
    combined["value_new"] = combined["value_new"].fillna(0)
    combined["existing"] = combined["value_tot"] - combined["value_new"]

    st.subheader("Installed capacity by technology")

    view = st.radio("Show", ["Existing + New", "Total only", "New only"], horizontal=True)

    y_cols = {
        "Existing + New": ["existing", "value_new"],
        "Total only":  ["value_tot"],
        "New only":    ["value_new"],
    }

    fig = px.bar(
        combined,
        x="g",
        y=y_cols[view],
        labels={"g": "Technology", "value": "Capacity (GW)", "variable": "Type"},
        height=700,
    )
    st.plotly_chart(fig, use_container_width=True)

# --------------------- CHARTS (By zones) ------------------
with open("../intermediate_data/region/shapes/europe_onshore.geojson") as f:
    geo = json.load(f)

# Aggregate
total_by_zone = (
    data["var_tot_pcap_z"]
    .groupby("z")["value"]
    .sum()
    .reset_index(name="total")
)

new_by_zone = (
    data["var_new_pcap_z"]
    .groupby("z")["value"]
    .sum()
    .reset_index(name="new")
)

# --- Total ---
with col2:
    st.subheader("Capacity by zone")

    tot_z = data["var_tot_pcap_z"]
    new_z = data["var_new_pcap_z"]

    # Aggregate by zone and technology
    total = (
        tot_z.groupby(["z", "g"])["value"]
        .sum()
        .reset_index(name="total")
    )

    new = (
        new_z.groupby(["z", "g"])["value"]
        .sum()
        .reset_index(name="new")
    )

    zone_cap = total.merge(new, on=["z", "g"], how="left")
    zone_cap["new"] = zone_cap["new"].fillna(0)
    zone_cap["existing"] = zone_cap["total"] - zone_cap["new"]

    # Controls
    cap_type = st.radio(
        "Capacity type",
        ["Total", "New", "Existing"],
        horizontal=True,
    )

    techs = sorted(zone_cap["g"].unique())

    selected_tech = st.selectbox(
        "Technology",
        ["All"] + techs
    )

    # Filter
    plot_data = zone_cap.copy()

    if selected_tech != "All":
        plot_data = plot_data[plot_data["g"] == selected_tech]

    # Sum over technologies if needed
    value_col = {
        "Total": "total",
        "New": "new",
        "Existing": "existing",
    }[cap_type]

    plot_data = (
        plot_data.groupby("z")[value_col]
        .sum()
        .reset_index()
    )

    fig_map = px.choropleth(
        plot_data,
        geojson=geo,
        locations="z",
        featureidkey="properties.index",
        color=value_col,
        color_continuous_scale="Blues",
        labels={value_col: "GW"},
        height=700
    )

    fig_map.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig_map, use_container_width=True)
