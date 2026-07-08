import streamlit as st
import plotly.express as px
from data.country_names import get_country_name
from data.constants import TECH_ICONS, area_reference
from ui.components import filter_countries


def render_land_usage(land_df, util_df, total_installed, total_potential):
    country_total_area = land_df["country_area_km2"].sum().round(1)

    st.subheader("Land Area Context")
    col1, col2, col3 = st.columns(3, border=True, gap="large")
    col1.metric(
        ":material/public: Total country land",
        f"{country_total_area:,.0f} km²",
        help="Sum of all country areas in the model",
    )
    col2.metric(
        ":material/landscape: VRE-suitable land",
        f"{total_potential:,.0f} km²",
        help="Land identified as technically suitable for VRE by the model",
    )
    col3.metric(
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
            x=["installed_area", "remaining_potential", "remaining_country"],
            y="country_name",
            orientation="h",
            color_discrete_map={
                "installed_area": "#2ECC71",
                "remaining_potential": "#A8D5B5",
                "remaining_country": "#E8E8E8",
            },
            labels={"value": "Area (km²)", "country_name": "Country", "variable": ""},
            height=700,
        )
        fig.update_layout(legend=dict(orientation="h", y=-0.1), barmode="stack")
        fig.update_traces(selector={"name": "installed_area"}, name="VRE installed")
        fig.update_traces(
            selector={"name": "remaining_potential"}, name="VRE potential (unused)"
        )
        fig.update_traces(
            selector={"name": "remaining_country"}, name="Rest of country"
        )
        st.plotly_chart(fig)

    with col_detail:
        _render_country_detail(land_df, util_df)

    st.divider()


def _render_country_detail(land_df, util_df):
    selected_country = st.selectbox(
        "Select country for breakdown",
        options=[None] + sorted(land_df["country_name"].unique()),
        format_func=lambda x: "Select a country..." if x is None else x,
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

    col1, col2, col3 = st.columns(3, border=True)
    col1.metric(
        ":material/public: Total country land",
        f"{country_row['country_area_km2']:,.0f} km²",
        help="Total land area of this country",
    )
    col2.metric(
        ":material/landscape: VRE-suitable land",
        f"{country_row['potential_area']:,.0f} km²",
        help="Land identified as technically suitable for VRE",
    )
    col3.metric(
        ":material/solar_power: Land used for VRE",
        f"{country_row['installed_area']:,.0f} km²",
        delta=f"{country_row['land_use_pct']}% of country land",
        help="Land actually occupied by newly installed VRE",
    )

    st.caption(f"Land occupied by newly installed renewables in {selected_country}:")

    for col, (_, row) in zip(
        st.columns(len(country_tech_df), border=True), country_tech_df.iterrows()
    ):
        t = row["g"]
        col.metric(
            f"{TECH_ICONS[t]} {t}",
            f"{row['installed']:,.1f} km²",
            f"{area_reference(row['installed'])}",
        )

    if excluded:
        st.info(f"Not shown (no installed capacity): {', '.join(sorted(excluded))}")
