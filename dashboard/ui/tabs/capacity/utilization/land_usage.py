import streamlit as st
import plotly.express as px
from data.constants import TECH_ICONS, area_reference
from ui.components import filter_countries


def render_land_usage(
    land_df,
    util_df,
    util_region_df,
    total_installed,
    total_potential,
):
    country_total_area = land_df["country_area_km2"].sum().round(1)

    st.subheader("Land Area Context")
    col1, col2 = st.columns(2, border=True, gap="large")
    col1.metric(
        ":material/public: Total zone land",
        f"{country_total_area:,.0f} km²",
        help="Sum of all zone areas in the model",
    )
    col2.metric(
        ":material/solar_power: Land used for VRE",
        f"{total_installed:,.0f} km²",
        help="Land actually occupied by newly installed VRE capacity",
    )

    col_chart, col_detail = st.columns([0.6, 0.4], gap="large")

    with col_chart:
        land_usage_filtered = filter_countries(
            land_df.sort_values("installed_area", ascending=True),
            default=[],
            key="filter_land_usage",
        )
        fig = px.bar(
            land_usage_filtered,
            x=["installed_area", "remaining_country"],
            y="country_name",
            orientation="h",
            color_discrete_map={
                "installed_area": "#2ECC71",
                "remaining_country": "#E8E8E8",
            },
            labels={"value": "Area (km²)", "country_name": "Zone", "variable": ""},
            height=700,
        )
        fig.update_layout(legend=dict(orientation="h", y=-0.1), barmode="stack")
        fig.update_traces(selector={"name": "installed_area"}, name="VRE installed")
        fig.update_traces(selector={"name": "remaining_country"}, name="Rest of zone")
        st.plotly_chart(fig)

    with col_detail:
        _render_country_detail(land_df, util_df, util_region_df)

    st.divider()


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

    st.subheader(selected_country)

    col1, col2 = st.columns(2, border=True, gap="large")
    col1.metric(
        ":material/public: Total zone land",
        f"{country_row['country_area_km2']:,.0f} km²",
        help="Total land of this zone",
    )
    col2.metric(
        ":material/solar_power: Land used for VRE",
        f"{country_row['installed_area']:,.0f} km²",
        delta=f"{country_row['land_use_pct']}% of total land area",
        help="Land actually occupied by newly installed VRE",
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

    table["Total"] = table.sum(axis=1)

    table = table.sort_values("Total", ascending=False)

    st.dataframe(table.style.format("{:.1f}"))

    # Display regions with nothing installed in infobox
    if inactive_regions:
        st.info("Not shown (no installed capacity): " + ", ".join(inactive_regions))
