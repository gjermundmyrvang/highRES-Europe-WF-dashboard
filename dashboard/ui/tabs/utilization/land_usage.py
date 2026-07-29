import streamlit as st
import pandas as pd
import plotly.express as px
from data.constants import TECH_ICONS, area_reference, TECH_COLORS
from ui.components import filter_countries
from ..shared.land_use_barchart import render_land_usage_bar


def render_land_usage(
    land_df,
    util_df,
    util_region_df,
):
    country_total_area = land_df["country_area_km2"].sum().round(1)

    st.subheader("Total Area Context")
    col1, col2 = st.columns([0.3, 0.7], border=True, gap="large")
    col1.metric(
        ":material/public: Total zone land",
        f"{country_total_area:,.0f} km²",
        help="Sum of all country areas in the model",
    )
    with col2:
        tech_total = util_df.groupby("g")["installed"].sum().reset_index()
        num_tech_cols = len(set(util_df["g"].unique()))
        for col, (_, row) in zip(
            st.columns(num_tech_cols, gap="large"), tech_total.iterrows()
        ):
            t = row["g"]
            icon = TECH_ICONS.get(t, ":material/category:")
            col.metric(
                f"{icon} {t}",
                f"{row['installed']:,.0f} km²",
            )

    render_land_usage_bar(util_df, land_df)

    st.space("small")

    col_chart, col_detail = st.columns([0.6, 0.4], gap="large")

    with col_chart:
        st.subheader("Zone Area Context")
        view = st.radio(
            "View as",
            options=["Absolute (km²)", "Percentage (%)"],
            horizontal=True,
        )

        # Apply filter
        filtered_df = filter_countries(util_df, [], key="filter_land_usage")

        # Aggregate installed area per country and tech
        tech_country = (
            filtered_df.groupby(["country_name", "g"])["installed"].sum().reset_index()
        )

        # Add remaining country land
        country_totals = (
            tech_country.groupby("country_name")["installed"].sum().reset_index()
        )
        country_totals = country_totals.merge(
            land_df[["country_name", "country_area_km2"]], on="country_name", how="left"
        )
        country_totals["remaining"] = (
            country_totals["country_area_km2"] - country_totals["installed"]
        )

        # Add remaining as a "tech"
        remaining_df = country_totals[["country_name", "remaining"]].rename(
            columns={"remaining": "installed"}
        )
        remaining_df["g"] = "Unused land"
        tech_country = pd.concat([tech_country, remaining_df], ignore_index=True)

        # Sort countries by total installed
        sort_order = country_totals.sort_values("installed", ascending=False)[
            "country_name"
        ].tolist()

        color_map = {**TECH_COLORS, "Unused land": "#E8E8E8"}

        if view == "Percentage (%)":
            # Convert installed to % of country area
            tech_country = tech_country.merge(
                land_df[["country_name", "country_area_km2"]],
                on="country_name",
                how="left",
            )
            tech_country["installed"] = (
                tech_country["installed"] / tech_country["country_area_km2"] * 100
            )
            x_label = "%"
        else:
            x_label = "km²"

        fig = px.bar(
            tech_country,
            x="installed",
            y="country_name",
            color="g",
            orientation="h",
            color_discrete_map=color_map,
            labels={"installed": x_label, "country_name": "Country", "g": "Technology"},
            height=700,
            category_orders={"country_name": sort_order},
        )
        fig.update_layout(barmode="stack", legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig)

    with col_detail:
        st.subheader("Zone Breakdown")
        _render_country_detail(land_df, util_df, util_region_df)


def _render_country_detail(land_df, util_df, util_region_df):
    selected_country = st.selectbox(
        "Select zone for breakdown",
        options=[None] + sorted(land_df["country_name"].unique()),
        format_func=lambda x: "Select a zone..." if x is None else x,
    )

    if not selected_country:
        return

    country_tech_df = util_df[util_df["country_name"] == selected_country].copy()
    country_tech_df = country_tech_df[
        (country_tech_df["installed"] > 0) & (country_tech_df["installed"].notna())
    ]

    all_techs = set(util_df[util_df["country_name"] == selected_country]["g"])
    shown_techs = set(country_tech_df["g"])
    excluded = all_techs - shown_techs

    country_row = land_df[land_df["country_name"] == selected_country].iloc[0]
    selected_z = country_row["z"]

    st.metric(
        ":material/public: Total zone land",
        f"{country_row['country_area_km2']:,.0f} km²",
        help="Total land of this country",
    )

    st.caption(f"Land occupied by newly installed renewables in {selected_country}:")

    # Technologies
    for col, (_, row) in zip(
        st.columns(len(country_tech_df), border=True, gap="large"),
        country_tech_df.iterrows(),
    ):
        t = row["g"]
        icon = TECH_ICONS.get(t, ":material/category:")
        delta_str = f"{area_reference(row['installed'])}"
        col.metric(
            f"{icon} {t}",
            f"{row['installed']:,.1f} km²",
            delta=delta_str,
        )

    if excluded:
        st.info(f"Not shown (no installed capacity): {', '.join(sorted(excluded))}")

    # Land usage barchart
    render_land_usage_bar(util_df, land_df, selected_z)

    # Regional Data
    st.caption("Land occupied by newly installed renewables in regions")
    region_df = util_region_df[
        util_region_df["country_name"] == selected_country
    ].copy()

    region_totals = region_df.groupby("r")["installed"].sum()
    inactive_regions = region_totals[region_totals == 0].index.tolist()
    active_df = region_df[region_df["r"].isin(region_totals[region_totals > 0].index)]
    table = active_df.pivot_table(
        index="r",
        columns="g",
        values="installed",
        aggfunc="sum",
        fill_value=0,
    )

    highlight = st.radio(
        "Highlight",
        ["Max", "Min", "None"],
        horizontal=True,
        index=2,
        key="radio_regions_land_usage",
    )

    table["Total"] = table.sum(axis=1)

    table = pd.DataFrame(table.sort_values("Total", ascending=False))
    table.style.format("{:.1f}")

    if highlight == "None":
        table = table.style.highlight_null()
    elif highlight == "Max":
        table = table.style.highlight_max(axis=0)
    else:
        table = table.style.highlight_min(axis=0)

    st.dataframe(table)

    # Display regions with nothing installed in infobox
    if inactive_regions:
        st.info("Not shown (no installed capacity): " + ", ".join(inactive_regions))
