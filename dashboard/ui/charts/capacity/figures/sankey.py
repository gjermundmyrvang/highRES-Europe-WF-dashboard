import streamlit as st
import plotly.graph_objects as go
from data.tech_colors import TECH_COLORS

def render_sankey(df):    
    # Sum installed and potential per technology across all countries
    tech_agg = df.groupby("g")[["installed", "potential"]].sum()
    # Unused = what's available but not built
    tech_agg["unused"] = tech_agg["potential"] - tech_agg["installed"]

    techs = sorted(df["g"].unique())
    n_techs = len(techs)

    # Node labels
    labels = ["Total Potential (VRE)"] + techs + ["Installed", "Unused"]

    # Source: Total Potential (0) → each tech node
    source = [0] * n_techs
    target = list(range(1, n_techs + 1))
    value = tech_agg["potential"].tolist()
    link_colors = (
    ["rgba(100,100,100,0.3)"] * n_techs  # Total Potential → each tech
    )

    # Each tech → Installed and Unused
    installed_idx = n_techs + 1
    unused_idx = n_techs + 2

    for i, tech in enumerate(techs):
        source += [i + 1, i + 1]
        target += [installed_idx, unused_idx]
        value += [tech_agg.loc[tech, "installed"], tech_agg.loc[tech, "unused"]]
        # installed=green, unused=red
        link_colors += ["rgba(50,200,50,0.5)", "rgba(200,50,50,0.3)"] 

    node_colors = (
        ["#d3d3d3"]  # Total Potential
        + [TECH_COLORS.get(t, "#d3d3d3") for t in techs]  # one color per tech
        + ["rgba(50,200,50,0.8)", "rgba(200,50,50,0.8)"]  # Installed, Unused
    )
    fig = go.Figure(go.Sankey(
        node=dict(label=labels, hovertemplate="%{label}: %{value:.1f} GW<extra></extra>", color=node_colors,),
        link=dict(source=source, target=target, value=value, hovertemplate="%{source.label} → %{target.label}: %{value:.1f} GW<extra></extra>",  color=link_colors,),
        textfont=dict(color="white", size=20),
    ))
    fig.update_layout(title="Potential vs installed/unused capacity flow", height=1200)
    st.plotly_chart(fig, use_container_width=True)