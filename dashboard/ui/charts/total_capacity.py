import streamlit as st
from plots.technology_bar import plot_tot_bars

def render_total_capicity(data):
    tot = data["var_tot_pcap"].copy()
    new = data["var_new_pcap"].copy()

    combined = tot.merge(new, on="g", how="left", suffixes=("_tot", "_new"))
    combined["value_new"] = combined["value_new"].fillna(0)
    combined["existing"] = combined["value_tot"] - combined["value_new"]

    st.subheader("Installed capacity by technology")

    view = st.radio("Show", ["Existing + New", "Total only", "New only"], horizontal=True)

    y_cols = {
        "Existing + New": ["existing", "value_new"],
        "Total only":  ["value_tot"],
        "New only":    ["value_new"],
    }

    fig = plot_tot_bars(combined, view, y_cols)
    st.plotly_chart(fig, use_container_width=True)