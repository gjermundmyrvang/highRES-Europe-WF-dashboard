import streamlit as st
from data.country_names import get_country_name
from data.utilization import calculate_utilization
from .figures import render_sankey, render_pivot, render_bar_chart


def render_dimension_two(tot_z, potential_z):
    st.subheader(
        "Dimension 2: How much of the available potential (GW) of VRE tech is utilized?"
    )
    st.markdown("Dataset: `var_new_pcap_z` & `area`")

    df = calculate_utilization(tot_z, potential_z)
    df["country_name"] = df["z"].apply(get_country_name)

    # Key Metrics
    _render_key_metrics(df)

    # Data comments
    with st.expander("Data comments"):
        st.info("""
            - Available potential (GW-values) from `area` is reported at the regional (`r`) level and aggregated to country (`z`) level before comparison. 
            - Utilization is then calculated for each country-technology pair (`z`, `g`) as: `Utilization (%) = Installed Capacity / Available Potential × 100`
            - Missing installed capacity values are treated as 0
            """)

        st.warning("""
            Data note: All `HydroRoR` potential values in the `area` dataset are stored as `+INF`. These values are replaced with missing values (`NaN`)
            before analysis.
            """)

    # Charts
    st.subheader("Utilization of VRE technologies:")

    render_pivot(df)
    render_bar_chart(df)


def _render_key_metrics(df):
    st.subheader("Key Metrics")
    installed_total = df["installed"].sum()
    potential_total = df["potential"].sum()

    # Ratio of total installed to total potential.
    system_util = (installed_total / potential_total) * 100

    # Top summary row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Installed VRE Capacity",
            f"{installed_total:,.0f} GW",
            delta="Total capacity",
        )

    with col2:
        st.metric(
            "Total VRE Potential",
            f"{potential_total:,.0f} GW",
            delta="Potential capacity",
        )

    with col3:
        st.metric(
            "System Utilization",
            f"{system_util:.1f}%",
        )
