import streamlit as st
import plotly.express as px
from ui.components import filter_countries


def render_pivot(df):
    # Installed / potential (across techs) per country
    filtered_pivot = filter_countries(
        df, [], "filter_pivot"
    )  # '[]' returns just all countries
    pivot = filtered_pivot.pivot(
        index="country_name", columns="g", values="utilization_pct"
    )

    # Heatmap viz for country tech combinations
    fig = px.imshow(
        pivot,
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale="blues",
        height=600,
    )
    fig.update_layout(xaxis_title="Technology", yaxis_title=None)
    st.plotly_chart(fig)

    with st.expander("See data table (raw)"):
        st.dataframe(filtered_pivot)

    with st.expander("See data table (pivot)"):
        st.dataframe(pivot)
