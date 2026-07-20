import streamlit as st
from ..figures import (
    render_tech_bar_chart,
    render_country_bar_chart,
    render_pivot,
)


def render_breakdown(util_df, unit_label):
    col_tech, col_bar, col_pivot = st.columns(3, gap="large")

    with col_tech:
        st.caption("BY TECHNOLOGY")
        tech_df = util_df.groupby("g")[["installed", "potential"]].sum().reset_index()
        tech_df["util_pct"] = (
            (tech_df["installed"] / tech_df["potential"] * 100).clip(upper=100).round(1)
        )
        tech_df["unused_pct"] = 100 - tech_df["util_pct"]
        tech_df = tech_df.sort_values("util_pct", ascending=True)

        render_tech_bar_chart(tech_df, unit_label)

    with col_bar:
        st.caption("BY COUNTRY")
        country_df = (
            util_df.groupby(["z", "country_name"])[["installed", "potential"]]
            .sum()
            .reset_index()
        )
        country_df["util_pct"] = (
            (country_df["installed"] / country_df["potential"] * 100)
            .clip(upper=100)
            .round(1)
        )
        country_df = country_df.sort_values("util_pct", ascending=True)

        render_country_bar_chart(country_df, unit_label)

    with col_pivot:
        st.caption("BY COUNTRY & TECH")
        render_pivot(util_df)
