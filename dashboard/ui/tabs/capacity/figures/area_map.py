import streamlit as st
import plotly.express as px

def render_area_map(df, geo):
    fig = px.choropleth(
        df,
        geojson=geo,
        locations="z",
        featureidkey="properties.index",
        color="utilization_pct",
        color_continuous_scale="Greens",
        hover_name="z",
        hover_data={
            "z": False,
            "potential_area": ":.1f",
            "installed_area": ":.1f",
            "utilization_pct": ":.1f",
        },
        title="VRE area utilization by country (%)",
        labels={
        "utilization_pct": "Utilization (%)",
        "potential_area": "Potential area (km²)",
        "installed_area": "Installed area (km²)",
    },
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=800)
    
    selected = st.plotly_chart(fig, on_select="rerun", key="map") # Workaround for click-to-select

    return selected