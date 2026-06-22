import streamlit as st
import plotly.express as px
from ui.components import filter_countries

def render_bar_chart(df):
    # Bar chart country ranking
    filtered_bar = filter_countries(df, [], "filter_barchart")
    country_util = filtered_bar.groupby("country_name").apply(
        lambda x: x["installed"].sum() / x["potential"].sum() * 100
    ).reset_index(name="utilization_pct")
    country_util_sorted = country_util.sort_values("utilization_pct", ascending=True)
    avg_util_country = country_util["utilization_pct"].mean()
    
    fig = px.bar(
        country_util_sorted,
        x="utilization_pct",
        y="country_name",
        orientation="h",
        title="Total utilization per country (installed / potential)",
        labels={"utilization_pct": "Utilization (%)",},
        height=800
    )
    fig.update_yaxes(title=None)
    fig.update_xaxes(
        dtick=2,
    )
    fig.add_vline(
        x=avg_util_country,
        line_width=2,
        line_dash="dash",
        line_color="red"
    )
    fig.add_annotation(
        x=avg_util_country,
        y=1,
        yref="paper",
        text=f"Mean: {avg_util_country:.1f}%",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(color="red")
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("See data table"):
        st.dataframe(country_util.sort_values("utilization_pct", ascending=False))