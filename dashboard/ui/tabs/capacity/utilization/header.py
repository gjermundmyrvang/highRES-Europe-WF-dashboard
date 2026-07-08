import streamlit as st


def render_utilization_header():
    st.caption("How much of the available renewable potential did the model build?")
    with st.expander("How utilization is calculated", expanded=True):
        st.markdown("""
        **Installed capacity** comes from `var_new_pcap_z` --> only newly built VRE technologies (Solar, Wind Onshore, Wind Offshore).
        
        **Available potential** comes from the `area` dataset, which reports the maximum installable capacity per country and technology based on land availability and resource quality.
        
        - `HydroRoR` is excluded as its potential is stored as `+INF`
        - **Power (GW)**: direct comparison of installed vs potential capacity
        - **Area (km²)**: capacity values converted using technology-specific factors:
            - Solar: 0.04 GW/km²
            - Wind Onshore: 0.0024 GW/km²
            - Wind Offshore: 0.005 GW/km²
        """)

    unit = st.radio(
        "Show results in",
        options=["Power (GW)", "Area (km²)"],
        horizontal=True,
    )

    use_area = unit == "Area (km²)"
    unit_label = "km²" if use_area else "GW"

    # Only want to show country land data if area unit is focused
    show_land_pct = False
    if use_area:
        show_land_pct = st.checkbox("Compare against total country land area")
    else:
        st.checkbox(
            "Compare against total country land area", disabled=True, value=False
        )

    return unit, use_area, show_land_pct, unit_label
