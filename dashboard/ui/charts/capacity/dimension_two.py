import streamlit as st
import numpy as np
import plotly.express as px

def _calculate_utilization(tot_z, potential_z):
    vre_techs = set(potential_z["g"].unique())
    installed_vre = tot_z[tot_z["g"].isin(vre_techs)]
 
    installed_agg = (
        installed_vre
        .groupby(["z", "g"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "installed"})
    )
 
    potential_agg = (
        potential_z
        .groupby(["z", "g"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "potential"})
    )
 
    df = installed_agg.merge(potential_agg, on=["z", "g"], how="inner")
 
    df["utilization_pct"] = np.where(
        df["potential"] > 0,
        df["installed"] / df["potential"] * 100,
        np.nan,
    )
 
    return df

def render_dimension_two(tot_z, potential_z):
    st.subheader("Dimension 2: How much of the available potential is utilized?")
    st.text("Dataset: var_tot_pcap_z & area")
 
    df = _calculate_utilization(tot_z, potential_z)
 
    # Key metrics
    st.write("Installed total:", round(df["installed"].sum()), "GW")
    st.write("Potential total:", round(df["potential"].sum()), "GW")
    st.metric(
        "Average utilization (tech-country pairs)",
        f"{df['utilization_pct'].mean():.1f}%",
    )
    st.metric(
        "Average utilization (across countries)",
        f"{df.groupby('z')['utilization_pct'].mean().mean():.1f}%",
    )
    st.metric(
        "System-wide utilization (installed vs potential)",
        f"{(df['installed'].sum() / df['potential'].sum()) * 100:.1f}%",
    )
 
    # Charts
    st.subheader("Utilization of VRE technologies:")
    pivot = df.pivot(index="z", columns="g", values="utilization_pct")
 
    fig = px.imshow(
        pivot,
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale="Viridis",
        height=800,
    )
    st.plotly_chart(fig, use_container_width=True)
 
    fig = px.bar(
        df,
        x="utilization_pct",
        y="z",
        color="g",
        orientation="h",
        barmode="stack",
        height=800,
    )
    st.plotly_chart(fig, use_container_width=True)
 
    with st.expander("See data table (pivot)"):
        st.dataframe(pivot)