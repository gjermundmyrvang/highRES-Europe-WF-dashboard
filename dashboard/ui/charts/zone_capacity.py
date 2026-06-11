import streamlit as st
from data.transformer import build_zone_capacity
from plots.capacity_map import plot_zone_map

def render_zone_capicity(data, geo):
    st.subheader("Capacity by zone")

    tot_z = data["var_tot_pcap_z"]
    new_z = data["var_new_pcap_z"]

    zone_cap = build_zone_capacity(tot_z, new_z)

    # Controls
    cap_type = st.radio(
        "Capacity type",
        ["Total", "New", "Existing"],
        horizontal=True,
    )

    techs = sorted(zone_cap["g"].unique())

    selected_tech = st.selectbox(
        "Technology",
        ["All"] + techs
    )

    # Filter
    plot_data = zone_cap.copy()

    if selected_tech != "All":
        plot_data = plot_data[plot_data["g"] == selected_tech]

    # Sum over technologies if needed
    value_col = {
        "Total": "total",
        "New": "new",
        "Existing": "existing",
    }[cap_type]

    plot_data = (
        plot_data.groupby("z")[value_col]
        .sum()
        .reset_index()
    )

    fig_map = plot_zone_map(plot_data, geo, value_col)
    st.plotly_chart(fig_map, use_container_width=True)


