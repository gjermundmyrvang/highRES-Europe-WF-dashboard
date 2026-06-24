import streamlit as st
import plotly.express as px
from ui.components import filter_countries

def render_country_scatter(df):
    filtered = filter_countries(df, default=[], key="filter_scatterplot")
    
    col1, col2 = st.columns(2, border=True)
    with col1:
        _render_util_scatter(filtered)

    with col2:
        _render_area_usage_scatter(filtered)
        


def _render_util_scatter(df):
    median = df["utilization_pct"].median()

    fig = px.scatter(
        df,
        x="z",
        y="utilization_pct",
        title="% of country area utilized by VRE tech",
        labels={
            "z": "Country",
            "utilization_pct": "Percentage of land area utilized",
        },
    )
    fig.add_hline(
        y=median,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Median: {median:.1f}%",
        annotation_position="top right",
    )
    st.plotly_chart(fig)

def _render_area_usage_scatter(df):
    fig = px.scatter(
        df,
        x="installed_area",
        y="potential_area",
        size="utilization_pct",
        hover_data=["z"],
        title="Country potential vs installed area",
        labels={
            "installed_area": "Installed Area (km2)",
            "potential_area": "Potential Area (km2)",
        },
    )
    st.plotly_chart(fig)

