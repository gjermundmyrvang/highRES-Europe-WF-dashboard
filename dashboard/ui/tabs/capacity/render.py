import streamlit as st
import numpy as np
from data.utilization import calculate_utilization, calculate_country_land_use
from data.country_names import get_country_name
from data.constants import VRE_TECHS
from .figures import (
    render_capacity_pies,
)
from ui.components import filter_countries
from data.constants import TECH_ICONS
from ..shared import render_key_data
from .utilization import (
    render_utilization_header,
    render_vre_summary,
    render_breakdown,
    render_land_usage,
)


def render_capacity(df, sets):
    # ----- CAPACITY --------
    st.title("Capacity Data")

    render_key_data(df)

    _render_capacity_overview(df, sets)

    st.divider()

    # ----- UTILIZATION --------
    st.title("Renewable Energy Deployment")
    _render_utilization(df)


def _render_capacity_overview(df, sets):
    cap_type = st.radio(
        "Capacity type",
        options=["Total", "New"],
        horizontal=True,
    )
    var = "var_tot_pcap_z" if cap_type == "Total" else "var_new_pcap_z"
    all = (
        df[var]
        .groupby("country_name")["value"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    # Top 5 countries by total installed
    top5 = all.head(5)

    col_countries, col_util = st.columns(2, gap="large")

    with col_countries:
        with st.container(border=True):
            st.caption("TOP 5 COUNTRIES BY INSTALLED CAPACITY")
            for i, row in top5.iterrows():
                st.metric(
                    f"{i + 1}.{row['country_name']}",
                    f"{row['value']:.0f} GW",
                )
            with st.expander(":material/public: &nbsp; See all"):
                st.dataframe(all)

    with col_util:
        with st.container(border=False):
            st.caption(f"{cap_type.upper()} INSTALLED CAPACITY BY TECHNOLOGY")
            var = "var_tot_pcap" if cap_type == "Total" else "var_new_pcap"
            tech_totals = (
                df[var]
                .groupby("g")["value"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            vre = tech_totals[tech_totals["g"].isin(VRE_TECHS)]
            non_vre = tech_totals[~tech_totals["g"].isin(VRE_TECHS)]

            sub1, sub2 = st.columns(2, border=True, gap="large")
            with sub1:
                st.caption("Renewable Technologies")
                for _, row in vre.iterrows():
                    icon = TECH_ICONS.get(row["g"], ":material/category:")
                    st.metric(f"{icon} {row['g']}", f"{row['value']:.1f} GW")
            with sub2:
                st.caption("Other Technologies")
                for _, row in non_vre.iterrows():
                    icon = TECH_ICONS.get(row["g"], ":material/category:")
                    st.metric(f"{icon} {row['g']}", f"{row['value']:.1f} GW")

    # Explore installed pcap
    _render_explore_installed_pcap(df, cap_type, top5)


def _render_explore_installed_pcap(df, cap_type, top5):
    st.subheader("What's been installed by countries?")

    tech_filter = st.radio(
        "Technologies",
        options=["All", "Renewables only"],
        horizontal=True,
    )

    var = "var_tot_pcap_z" if cap_type == "Total" else "var_new_pcap_z"
    focused = df[var]

    show_vre_only = tech_filter == "Renewables only"
    if show_vre_only:
        df_filtered = focused[focused["g"].isin(VRE_TECHS)]
    else:
        df_filtered = focused

    top5list = top5["country_name"].tolist()

    col1, col2 = st.columns([3, 1])
    with col1:
        filtered = filter_countries(df_filtered, top5list, key="filter_tot_pcap")
    with col2:
        cols = st.slider("Columns", min_value=1, max_value=6, value=5)

    fig = render_capacity_pies(filtered, cols=cols)
    st.plotly_chart(fig)

    with st.expander("See data table"):
        st.dataframe(filtered)


def _render_utilization(df):
    # Header
    unit, use_area, show_land_pct, unit_label = render_utilization_header()

    # Data preparation
    potential_z = df["area"].replace([np.inf, -np.inf], np.nan)
    new_vre_z = df["var_new_pcap_z"]

    util_df = calculate_utilization(new_vre_z, potential_z, use_area=use_area)

    total_installed = util_df["installed"].sum().round(1)
    total_potential = util_df["potential"].sum().round(1)
    util_pct = (total_installed / total_potential * 100).round(1)
    util_pct = float(util_pct) if not np.isnan(util_pct) else 0.0

    # LAND USAGE
    if show_land_pct:
        land_df = calculate_country_land_use(new_vre_z, potential_z)
        render_land_usage(land_df, util_df, total_installed, total_potential)

    # VRE aggregated
    render_vre_summary(
        util_df, total_installed, total_potential, util_pct, unit_label, unit
    )

    # By technology + by country + by both
    render_breakdown(util_df, unit_label)
