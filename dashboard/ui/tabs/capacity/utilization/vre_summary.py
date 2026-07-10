import streamlit as st
import numpy as np
from data.constants import TECH_ICONS


def render_vre_summary(
    util_df, total_installed, total_potential, util_pct, unit_label, unit
):
    st.subheader("System Overview")
    st.caption(f"Using {unit_label} as unit")
    total_col, vre_col = st.columns([0.3, 0.7])
    with total_col:
        st.markdown("#### All VRE combined")
        with st.container(border=True):
            st.metric(
                "New Installed VRE",
                f"{total_installed:,.0f} {unit_label}",
            )
            st.progress(
                float(util_pct / 100),
                text=f"{util_pct}% of potential: **{total_potential:,.0f}** {unit}",
            )

    with vre_col:
        st.markdown("#### By technology")
        with st.container(border=True):
            tech_df = (
                util_df.groupby("g")[["installed", "potential"]].sum().reset_index()
            )
            n_vre_cols = len(tech_df["g"])
            vre_cols = st.columns(n_vre_cols)
            for i in range(n_vre_cols):
                tech = tech_df.iloc[i]["g"]
                icon = TECH_ICONS[tech]
                installed = tech_df.iloc[i]["installed"]
                potential = tech_df.iloc[i]["potential"]
                util = (installed / potential * 100).round(1) if potential > 0 else 0.0
                util = float(util) if not np.isnan(util) else 0.0
                with vre_cols[i]:
                    st.metric(f"{icon} {tech}", value=f"{installed:,.0f} {unit_label}")
                    st.progress(
                        float(util / 100),
                        text=f"{util}% of potential: **{potential:,.0f}** {unit}",
                    )
