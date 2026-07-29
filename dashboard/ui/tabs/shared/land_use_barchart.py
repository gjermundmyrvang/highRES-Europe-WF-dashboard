import streamlit as st
from data.constants import TECH_COLORS


def render_land_usage_bar(util_df, land_df, country=None):
    df = util_df.copy()
    if country:
        df = df[df["z"] == country]
        total_area = land_df[land_df["z"] == country]["country_area_km2"].iloc[0]
    else:
        total_area = land_df["country_area_km2"].sum()

    tech_total = df.groupby("g")["installed"].sum().reset_index()
    segments = ""
    for _, row in tech_total.iterrows():
        pct = row["installed"] / total_area * 100
        color = TECH_COLORS.get(row["g"], "#cccccc")
        segments += f'<div style="width:{pct:.3f}%;background:{color};height:24px;display:inline-block;" title="{row["g"]}: {pct:.2f}%"></div>'

    remaining_pct = 100 - tech_total["installed"].sum() / total_area * 100
    segments += f'<div style="width:{remaining_pct:.3f}%;background:#E8E8E8;height:24px;display:inline-block;" title="Unused"></div>'

    st.markdown(
        f'<div style="width:100%;border-radius:4px;overflow:hidden;display:flex;">{segments}</div>',
        unsafe_allow_html=True,
    )
