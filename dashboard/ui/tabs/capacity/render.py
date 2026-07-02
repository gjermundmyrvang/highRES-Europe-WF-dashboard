import streamlit as st
import numpy as np
import plotly.express as px
from data.utilization import calculate_utilization
from data.country_names import get_country_name
from data_loader import table
from .figures import render_capacity_pies, render_pivot, render_bar_chart
from ui.components import filter_countries
from data.constants import TECH_ICONS
from ..shared import render_key_data


def render_capacity(df, sets):
    # ----- CAPACITY --------
    st.title("Capacity Data")

    render_key_data(df, sets)

    _render_capacity_overview(df, sets)

    st.divider()

    # ----- UTILIZATION --------
    st.title("Utilization of VRE")
    _render_utilization(df)


def _render_capacity_overview(df, sets):
    all = (
        df["var_tot_pcap_z"]
        .groupby("z")["value"]
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
                    f"{i + 1}.{get_country_name(row['z'])}",
                    f"{row['value']:.0f} GW",
                )
            with st.expander(":material/public: &nbsp; See all"):
                st.dataframe(all)

    with col_util:
        with st.container(border=False):
            st.caption("INSTALLED CAPACITY BY TECHNOLOGY")

            cap_type = st.radio(
                "Capacity type",
                options=["Total", "New"],
                horizontal=True,
            )
            var = "var_tot_pcap" if cap_type == "Total" else "var_new_pcap"
            tech_totals = (
                df[var]
                .groupby("g")["value"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            vre_techs = table(sets, "vre")["g"].tolist()
            vre = tech_totals[tech_totals["g"].isin(vre_techs)]
            non_vre = tech_totals[~tech_totals["g"].isin(vre_techs)]

            sub1, sub2 = st.columns(2, border=True, gap="large")
            with sub1:
                st.caption("VRE")
                for _, row in vre.iterrows():
                    icon = TECH_ICONS.get(row["g"], ":material/category:")
                    st.metric(f"{icon} {row['g']}", f"{row['value']:.1f} GW")
            with sub2:
                st.caption("Other")
                for _, row in non_vre.iterrows():
                    icon = TECH_ICONS.get(row["g"], ":material/category:")
                    st.metric(f"{icon} {row['g']}", f"{row['value']:.1f} GW")

    # Explore installed pcap
    _render_explore_installed_pcap(df, top5)


def _render_explore_installed_pcap(df, top5):
    st.subheader("Whats been installed by countries?")

    tot_z = df["var_tot_pcap_z"]
    new_z = df["var_new_pcap_z"]

    selected_table = st.radio(
        "Select focused table",
        options=["`var_tot_pcap_z`", "`var_new_pcap_z`"],
        horizontal=True,
    )

    focused = tot_z if selected_table == "var_tot_pcap_z" else new_z

    top5list = top5["z"].tolist()

    col1, col2 = st.columns([3, 1])
    with col1:
        filtered = filter_countries(focused, top5list, key="filter_tot_pcap")
    with col2:
        cols = st.slider("Columns", min_value=1, max_value=6, value=5)

    fig = render_capacity_pies(filtered, cols=cols)
    st.plotly_chart(fig)

    with st.expander("See data table"):
        st.dataframe(filtered)


def _render_utilization(df):
    st.caption("How much of the available VRE potential has the model installed?")
    with st.expander("How utilization is calculated"):
        st.markdown("""
        **Installed capacity** comes from `var_new_pcap_z` --> only newly built VRE technologies (Solar, Wind Onshore, Wind Offshore).
        
        **Available potential** comes from the `area` dataset, which reports the maximum installable capacity per country and technology based on land availability and resource quality.
        
        - `HydroRoR` is excluded as its potential is stored as `+INF`
        - **Power (GW)**: direct comparison of installed vs potential capacity
        - **Area (km²)**: capacity values converted using technology-specific factors:
            - Solar: 1 km² can support 0.04 GW
            - Wind Onshore: 1 km² can support 0.0024 GW
            - Wind Offshore: 1 km² can support 0.005 GW
        """)

    unit = st.radio(
        "View utilization in",
        options=["Power (GW)", "Area (km²)"],
        horizontal=True,
    )

    use_area = unit == "Area (km²)"
    unit_label = "km²" if use_area else "GW"

    # Data preparation
    potential_z = df["area"].replace([np.inf, -np.inf], np.nan)
    new_vre_z = df["var_new_pcap_z"]

    util_df = calculate_utilization(new_vre_z, potential_z, use_area=use_area)

    total_installed = util_df["installed"].sum().round(1)
    total_potential = util_df["potential"].sum().round(1)
    util_pct = (total_installed / total_potential * 100).round(1)
    util_pct = float(util_pct) if not np.isnan(util_pct) else 0.0

    # VRE aggregated
    total_col, vre_col = st.columns([0.3, 0.7])
    with total_col:
        st.subheader("Aggregated new VRE")
        with st.container(border=True):
            st.metric(
                "Total VRE",
                f"{total_installed:,.0f} {unit_label}",
            )
            st.progress(float(util_pct / 100), text=f"{util_pct}% of potential {unit}")

    with vre_col:
        st.subheader("By new VRE")
        with st.container(border=True):
            tech_df = (
                util_df.groupby("g")[["installed", "potential"]].sum().reset_index()
            )
            n_vre_cols = len(tech_df["g"])
            vre_cols = st.columns(n_vre_cols)
            for i in range(n_vre_cols):
                tech = tech_df.iloc[i]["g"]
                installed = tech_df.iloc[i]["installed"]
                potential = tech_df.iloc[i]["potential"]
                util = (installed / potential * 100).round(1)
                util = float(util) if not np.isnan(util) else 0.0
                with vre_cols[i]:
                    st.metric(tech, value=f"{installed.round(1)} {unit_label}")
                    st.progress(float(util / 100), text=f"{util}% of potential {unit}")

    # By technology + by country
    col_tech, col_bar, col_pivot = st.columns(3, gap="large")

    with col_tech:
        st.caption("BY TECHNOLOGY")
        tech_df = util_df.groupby("g")[["installed", "potential"]].sum().reset_index()
        tech_df["util_pct"] = (
            (tech_df["installed"] / tech_df["potential"] * 100).clip(upper=100).round(1)
        )
        tech_df["unused_pct"] = 100 - tech_df["util_pct"]
        tech_df = tech_df.sort_values("util_pct", ascending=True)

        fig = px.bar(
            tech_df,
            x=["util_pct", "unused_pct"],
            y="g",
            orientation="h",
            labels={
                "value": f"Utilization (%): {unit_label}",
                "g": "Technology",
                "variable": "",
            },
            color_discrete_map={"util_pct": "#2ECC71", "unused_pct": "#e0e0e0"},
            height=600,
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

    with col_bar:
        st.caption("BY COUNTRY")
        country_df = (
            util_df.groupby("z")[["installed", "potential"]].sum().reset_index()
        )
        country_df["util_pct"] = (
            (country_df["installed"] / country_df["potential"] * 100)
            .clip(upper=100)
            .round(1)
        )
        country_df = country_df.sort_values("util_pct", ascending=True)

        render_bar_chart(country_df, unit_label)

    with col_pivot:
        st.caption("BY COUNTRY & TECH")
        render_pivot(util_df)
