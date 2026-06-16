import streamlit as st
from plots.tot_trans_flow import plot_tot_trans_flow

def render_tot_trans_flow(data):
    st.subheader("Total Energy Transmissions")

    df = data["var_tot_trans_pcap"]

    # Filter on transtype and countries
    with st.expander("Filters", expanded=False):
        col1, col2 = st.columns(2)
 
        with col1:
            trans_options = sorted(df["trans"].unique())
            selected_trans = st.multiselect(
                "Transmission type",
                options=trans_options,
                default=trans_options,
            )
 
        with col2:
            all_countries = sorted(set(df["z"]) | set(df["z_alias"]))
            selected_countries = st.multiselect(
                "Filter by country (sender or receiver)",
                options=all_countries,
                default=["NO"], # Set default filter here or empty for all
                placeholder="All countries",
            )
 
    mask = df["trans"].isin(selected_trans)
    if selected_countries:
        mask &= df["z"].isin(selected_countries) | df["z_alias"].isin(selected_countries)
    filtered = df[mask]
 
    if filtered.empty:
        st.warning("No data matches the current filters.")
        return
 
    # Render chart
    fig = plot_tot_trans_flow(filtered)
    st.plotly_chart(fig, use_container_width="stretch")
 
    # raw data table 
    """with st.expander("Raw data"):   
        st.dataframe(
            filtered.sort_values("value", ascending=False).reset_index(drop=True),
            use_container_width="stretch",
        ) """