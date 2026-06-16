import streamlit as st
from plots.plot_capacity_pie import plot_capacity_pies

def render_zone_capicity_v2(data):
    st.subheader("Installed vs. Area Capacity")
    st.text("var_tot_pcap_z & area")

    tot_z = data["var_tot_pcap_z"]
    potential = data["area"]
    #new_z = data["var_new_pcap_z"]

    # ----- FILTERS -------
    col1, col2 = st.columns([3, 1])
    with col1:
        all_countries = sorted(set(tot_z["z"]))
        selected_countries = st.multiselect(
            "Filter countries",
            options=all_countries,
            default=["NO", "DK", "SE"],
        )
    with col2:
        cols = st.slider("Columns", min_value=2, max_value=6, value=3)
 
    filtered = tot_z[tot_z["z"].isin(selected_countries)]
    filtered_potential = potential[potential["z"].isin(selected_countries)]
 
    if filtered.empty:
        st.warning("No countries selected.")
        return
    
    # ----- CHARTS -------
    col3, col4 = st.columns(2)
    with col3: 
        st.markdown("#### Installed (PCAP)")
        fig = plot_capacity_pies(filtered, cols=cols)
        st.plotly_chart(fig, use_container_width="stretch")

    with col4:
        st.markdown("#### Area (VRE)")
        fig = plot_capacity_pies(filtered_potential, cols=cols)
        st.plotly_chart(fig, use_container_width="stretch")



    


