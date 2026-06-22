import streamlit as st
import plotly.express as px
import pandas as pd

def render_country_charts(country_df, total_installed, total_unused):
    col_pie, col_bar = st.columns([1, 2])

    with col_pie:
        st.caption("Total area --> used vs unused")
        fig = px.pie(
            pd.DataFrame({
                "Area": ["Used", "Unused"],
                "Area km²": [total_installed, total_unused],
            }),
            names="Area",
            values="Area km²",
            color="Area",
            color_discrete_map={"Used": "green", "Unused": "lightgrey"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width="stretch")

    with col_bar:
        st.caption("Area utilization by technology")
        fig = px.bar(
            country_df,
            x="g",
            y=["installed_area", "unused_area"],
            labels={"g": "Technology", "value": "Area (km²)", "variable": ""},
            barmode="stack",
            color_discrete_map={
                "installed_area": "green",
                "unused_area": "lightgrey",
            },
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width="stretch")