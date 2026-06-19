import streamlit as st
from plots.plot_capacity_pie import plot_capacity_pies

def _filter_countries(df):
    col1, col2 = st.columns([3, 1])
    with col1:
        all_countries = sorted(set(df["z"]))
        selected_countries = st.multiselect(
            "Filter countries",
            options=all_countries,
            default=["NO", "DK", "SE"],
        )
    with col2:
        cols = st.slider("Columns", min_value=2, max_value=6, value=3)
 
    filtered = df[df["z"].isin(selected_countries)]
 
    if filtered.empty:
        st.warning("No countries selected.")
        return None
 
    return {"filtered": filtered, "num_cols": cols}
 
 
# ── Dimension renderers ───────────────────────────────────────────────────────
 
def render_dimension_one(tot_z):
    st.subheader("Dimension 1: Explore whats been installed by countries?")
    st.text("Dataset: var_tot_pcap_z")
 
    filter_controls = _filter_countries(tot_z)
    if filter_controls is None:
        return
 
    filtered = filter_controls["filtered"]
    cols = filter_controls["num_cols"]
 
    fig = plot_capacity_pies(filtered, cols=cols)
    st.plotly_chart(fig, use_container_width="stretch")
 
    with st.expander("See data table"):
        st.dataframe(filtered)