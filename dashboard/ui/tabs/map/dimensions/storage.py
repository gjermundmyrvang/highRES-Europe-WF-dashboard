import streamlit as st

from data.transformer import random_hex_color
from .base import MapDimensionResult

LABEL = "Storage"


def render_controls(data, selected) -> tuple[MapDimensionResult, str]:
    all_storage = sorted(data["var_tot_store_pcap_z"]["s"].unique())
    disable_dropdown = selected is not None

    with st.container(border=True):
        selected_storage = st.selectbox(
            "Storage type", options=all_storage, disabled=disable_dropdown
        )

    df = data["var_tot_store_pcap_z"].copy()
    df = df[df["s"] == selected_storage]
    agg = df.groupby(["z", "country_name"])["value"].sum().reset_index()

    all_zones = data["var_tot_store_pcap_z"][["z", "country_name"]].drop_duplicates()
    agg = all_zones.merge(agg, on=["z", "country_name"], how="left").fillna(0)

    color = random_hex_color(selected_storage)

    return MapDimensionResult(df=agg, legend_label="GW", color=color), ""
