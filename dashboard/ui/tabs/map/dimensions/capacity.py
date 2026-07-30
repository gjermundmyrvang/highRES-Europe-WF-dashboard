import streamlit as st
from data.constants import TECH_COLORS
from .base import MapDimensionResult

LABEL = "Capacity"


def render_controls(data, selected) -> tuple[MapDimensionResult, str]:
    disable_dropdown = selected is not None

    with st.container(border=True):
        cap_type = st.radio(
            "Capacity type",
            options=["Total", "New"],
            horizontal=True,
            key="map_cap_type_radio",
        )

    var = "var_tot_pcap_z" if cap_type == "Total" else "var_new_pcap_z"
    source_df = data[var]

    all_techs = sorted(source_df["g"].unique())

    with st.container(border=True):
        selected_tech = st.selectbox(
            "Technology", options=all_techs, disabled=disable_dropdown
        )

    df = source_df[source_df["g"] == selected_tech]
    agg = df.groupby(["z", "country_name"])["value"].sum().reset_index()

    all_zones = source_df[["z", "country_name"]].drop_duplicates()
    agg = all_zones.merge(agg, on=["z", "country_name"], how="left").fillna(0)

    color = TECH_COLORS.get(selected_tech, "#1B5FA8")
    return MapDimensionResult(df=agg, legend_label="GW", color=color), var
