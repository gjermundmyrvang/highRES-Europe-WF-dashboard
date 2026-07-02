import streamlit as st
import plotly.express as px


def render_country_bar_chart(df, unit_label):
    mean = df["util_pct"].mean()
    show_mean = st.radio("Show mean?", options=["Yes", "No"], horizontal=True)
    fig = px.bar(
        df,
        x="util_pct",
        y="z",
        orientation="h",
        labels={"util_pct": f"Utilization (%): {unit_label}", "z": "Country"},
        color="util_pct",
        color_continuous_scale="Greens",
        range_color=[0, 100],
        height=600,
    )
    fig.update_layout(coloraxis_showscale=False)
    if show_mean == "Yes":
        fig.add_vline(
            x=mean,
            line_width=2,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean}%",
            annotation_position="bottom right",
        )

    st.plotly_chart(fig)


def render_tech_bar_chart(df, unit_label, x_vals=["util_pct", "unused_pct"]):
    fig = px.bar(
        df,
        x=x_vals,
        y="g",
        orientation="h",
        labels={
            "value": f"Utilization (%): {unit_label}",
            "g": "Technology",
            "variable": "",
        },
        color_discrete_map={"util_pct": "#2ECC71", "unused_pct": "#e0e0e0"},
        height=600,
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(texttemplate="%{x:.1f}%")
    st.plotly_chart(fig)
