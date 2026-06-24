import streamlit as st
from data.utilization import calculate_utilization, calculate_area_utilization
from data.country_names import get_country_name
from .figures import render_area_map, render_country_charts, render_country_scatter

def render_dimension_three(tot_z, potential_z, geo):
    st.subheader("Dimension 3: How much of area (km²) is used for VRE techs?")
    st.markdown("Dataset: `var_tot_pcap_z` & `area`")

    df = calculate_utilization(tot_z, potential_z)
    country_area = calculate_area_utilization(df)

    _render_key_metrics(country_area)
    with st.expander("Data comments"):
        st.info(
            """
            **How area utilization is calculated:**

            VRE potential (GW) from the `area` dataset is converted to land area (km²) 
            using a fixed factor of **1 km² = 2.4 GW**. This is applied to both installed 
            capacity and available potential for each country-technology pair.
            """
        )

    st.divider()
    render_country_scatter(country_area)


    col_map, col_metrics = st.columns([0.6, 0.4])
    with col_map:
        # Render map that returns clicked country
        selected = render_area_map(country_area, geo)

    with col_metrics:
        default_country = _get_selected_country(selected, country_area)
        selected_country = st.selectbox(
            "Select country for details",
            options=sorted(country_area["z"].unique()),
            index=sorted(country_area["z"].unique()).index(default_country),
        )
        country_df = df[df["z"] == selected_country]
        total_installed, total_unused = _render_country_metrics(country_df, selected_country)

    render_country_charts(country_df, total_installed, total_unused)

    with st.expander("Raw data"):
        st.dataframe(country_df)


def _render_key_metrics(df):
    st.subheader("Key Metrics")
    
    installed_area_total = df["installed_area"].sum()
    potential_area_total = df["potential_area"].sum()
    
    # Ratio of total installed to total potential.
    system_util = (installed_area_total / potential_area_total) * 100

    # Top summary row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Installed Area",
            f"{installed_area_total:,.0f} km²",
            delta="Total installed area"
        )

    with col2:
        st.metric(
            "Total Potential",
            f"{potential_area_total:,.0f} km²",
            delta="Total potential area"
        )

    with col3:
        st.metric(
            "System Utilization",
            f"{system_util:.1f}%",
        )

def _get_selected_country(selected, country_area):
    if selected and selected.selection.points:
        return selected.selection.points[0]["location"]
    return sorted(country_area["z"].unique())[0]

def _render_country_metrics(country_df, selected_country):
    st.subheader(f"Explore Area Utilization in: {get_country_name(selected_country)}")

    total_potential = country_df["potential_area"].sum()
    total_installed = country_df["installed_area"].sum()
    total_unused = country_df["unused_area"].sum()
    utilization = total_installed / total_potential * 100

    col1, col2 = st.columns(2)
    col1.metric("Potential Area", f"{total_potential:,.1f} km²")
    col1.metric("Utilization", f"{utilization:.1f}%")
    col2.metric("Used Area", f"{total_installed:,.1f} km²")
    col2.metric("Unused Area", f"{total_unused:,.1f} km²")

    return total_installed, total_unused
