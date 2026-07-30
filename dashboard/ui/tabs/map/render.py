import streamlit as st
import plotly.express as px

from data.constants import (
    TECH_ICONS,
    get_capacity_to_area,
    get_country_name,
)
from data.utilization import calculate_utilization_region
from ..shared.cost_breakdown import render_cost_breakdown
from .dimensions import DIMENSIONS


def render_map(data, geo, inflation_factor, selected_currency, rate, gbp_value):
    st.title("Map Exploration")
    st.markdown("> Displaying overview of installed capacity by technology in zones")
    st.info(
        body="**Click** any zone to view more in depth information about that zone.",
        icon=":material/ads_click:",
    )
    df = data["var_tot_pcap_z"]

    geo_indices = {f["properties"]["index"] for f in geo["features"]}
    z_values = set(df["z"].unique())
    matches = z_values & geo_indices

    if "map_selected_country" not in st.session_state:
        st.session_state.map_selected_country = None

    selected = st.session_state.map_selected_country
    if selected:
        selected_country_name = df[df["z"] == selected].iloc[0]["country_name"]

    if not matches:
        st.warning(
            "The zone codes in this scenario don't match the shapefile. "
            "A different shapefile may be needed --> check **`geojson_path`** in **`dashboard_config.yaml`**."
        )
        return

    if len(matches) < len(z_values):
        st.info(
            f"{len(z_values) - len(matches)} zone(s) couldn't be matched to the shapefile and won't appear on the map."
        )

    col_controls, col_map = st.columns([0.25, 0.75], gap="large")

    with col_controls:
        st.subheader(":material/tune: Controls")
        dimension_key = st.selectbox(
            "Dimension",
            options=list(DIMENSIONS.keys()),
            format_func=lambda k: DIMENSIONS[k].LABEL,
            key="map_dimension_select",
        )
        if DIMENSIONS[dimension_key].LABEL == "Cost":
            result = DIMENSIONS[dimension_key].render_controls(
                data, selected, inflation_factor, rate
            )

        else:
            result = DIMENSIONS[dimension_key].render_controls(data, selected)

    with col_map:
        header_str = f"{selected_country_name}" if selected else "Map"
        st.subheader(f":material/map: {header_str}")
        with st.container(border=True, height=800):
            if selected:
                if st.button(":material/arrow_back: Back to map"):
                    st.session_state.map_selected_country = None
                    st.rerun()
                _render_country_details(
                    data,
                    selected,
                    inflation_factor,
                    selected_currency,
                    rate,
                    gbp_value,
                )
            else:
                clicked = _render_map_viz(
                    result.df, geo, result.color, result.legend_label
                )
                if clicked:
                    st.session_state.map_selected_country = clicked
                    st.rerun()


def _render_map_viz(df, geo, color, legend_label):
    fig = px.choropleth(
        df,
        geojson=geo,
        locations="z",
        featureidkey="properties.index",
        color="value",
        color_continuous_scale=[
            [0, "#f0f0f0"],
            [0.001, "#e8f0fe"],
            [1, color],
        ],
        hover_name="country_name",
        labels={"value": legend_label},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=800, coloraxis_showscale=True)
    event = st.plotly_chart(fig, on_select="rerun")
    selected_country = _get_clicked_country(event)
    return selected_country


def _get_clicked_country(event) -> str | None:
    points = event["selection"].get("points", [])
    if points:
        first_point = points[0]
        return first_point["properties"].get("index", None)

    return None


def _render_country_details(
    data, country, inflation_factor, selected_currency, rate, gbp_value
):

    cap_type = st.radio(
        "Capacity type",
        options=["Total", "New"],
        horizontal=True,
        key="country_detail_cap_type_radio",
    )

    var = "var_tot_pcap_z" if cap_type == "Total" else "var_new_pcap_z"

    df = data[var]
    country_df = df[df["z"] == country].reset_index()

    # Installed techs
    st.subheader(f"Installed {cap_type} capacity")
    cols_per_row = 4
    cols = st.columns(cols_per_row, gap="large")
    for i, (_, row) in enumerate(country_df.iterrows()):
        t = row["g"]
        icon = TECH_ICONS.get(t, ":material/category:")
        cols[i % cols_per_row].metric(
            f"{icon} {t}", f"{row['value']:.1f} GW", border=True
        )

    st.divider()

    # Utilization (installed new vre vs potential)
    new_vre_df = data["var_new_vre_pcap_r"]
    potential_df = data["area"]
    vre_techs = set(new_vre_df["g"].unique())
    vre_list_str = ", ".join(vre_techs)
    st.subheader(
        "How much of potential renewable technology did the model build in this zone?"
    )
    st.info(
        f"Only {vre_list_str} are shown --> these are the technologies where the model defines an available potential to compare against."
    )
    cap2area = get_capacity_to_area(data)
    util_df = calculate_utilization_region(new_vre_df, potential_df, cap2area)
    country_util_df = util_df[util_df["z"] == country]
    pivot = country_util_df.pivot_table(
        index="r",
        columns="g",
        values="utilization_pct",
        fill_value=0,
    )
    fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        aspect="auto",
        labels={"color": "Utilization (%)"},
        text_auto=".0f",
    )
    fig.update_layout(
        xaxis_title="Technology",
        yaxis_title="Region",
        coloraxis_colorbar=dict(title="%"),
    )
    st.plotly_chart(fig)

    st.divider()

    # Zone Cost
    """
    IMPORTANT: 
    ------------------
    This section provides a zone to `render_cost_breakdown` function,
    but the actual breakdown of the transmission cost needs to be revised.
    """
    title_col, setting_col = st.columns(2)
    with title_col:
        st.subheader("Zone Costs")

    with setting_col:
        category = st.segmented_control(
            "Cost breakdown",
            options=["Generation", "Storage", "Transmission"],
            default="Generation",
            key="country_detail_costs_breakdown",
        )
    if category:
        render_cost_breakdown(
            data,
            category,
            inflation_factor,
            rate,
            selected_currency,
            gbp_value,
            country,
        )

    st.divider()

    st.subheader(f"Total Storage in {get_country_name(country)}")
    storage_df = (
        data["var_tot_store_pcap_z"].groupby(["z", "s"], as_index=False)["value"].sum()
    )
    storage_country_df = storage_df[storage_df["z"] == country].reset_index()
    cols_per_row = 4
    cols = st.columns(cols_per_row, gap="large")
    for i, (_, row) in enumerate(storage_country_df.iterrows()):
        s = row["s"]
        icon = ":material/category:"
        cols[i % cols_per_row].metric(
            f"{icon} {s}", f"{row['value']:.1f} GW", border=True
        )
