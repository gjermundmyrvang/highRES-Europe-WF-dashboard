import streamlit as st
from plots.technology_bar import plot_tot_bars

def render_total_capicity(data):
    st.subheader("Total capacity by technology")
    st.text("var_tot_pcap & var_new_pcap")
    
    tot = data["var_tot_pcap"].copy()
    new = data["var_new_pcap"].copy()

    combined = tot.merge(new, on="g", how="left", suffixes=("_tot", "_new"))
    combined["value_new"] = combined["value_new"].fillna(0)
    combined["existing"] = combined["value_tot"] - combined["value_new"]    

    fig = plot_tot_bars(combined)
    st.plotly_chart(fig, use_container_width="stretch")