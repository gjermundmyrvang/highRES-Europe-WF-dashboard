import plotly.graph_objects as go

def plot_tot_trans_flow(df):
    senders   = (df["z"]       + " (sender)").tolist()
    receivers = (df["z_alias"] + " (receiver)").tolist()

    all_nodes = list(dict.fromkeys(senders + receivers))   
    node_idx  = {n: i for i, n in enumerate(all_nodes)}

    TRANS_COLORS = {
        "HVAC_OHL":     "rgba(99, 149, 206, 0.75)",   
        "HVDC_MarineIC":"rgba(230, 126, 60,  0.75)",  
    }
    DEFAULT_COLOR = "rgba(160, 160, 160, 0.6)"
 
    link_colors = [
        TRANS_COLORS.get(t, DEFAULT_COLOR) for t in df["trans"]
    ]
 
    node_colors = [
        "#20c318" if n.endswith("(sender)") else "#bb0b2c"
        for n in all_nodes
    ]

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            label=all_nodes,
            color=node_colors,
            pad=18,
            thickness=18,
            line=dict(color="white", width=0.5),
        ),
        link=dict(
            arrowlen=15,
            source=[node_idx[s] for s in senders],
            target=[node_idx[r] for r in receivers],
            value=df["value"].tolist(),
            color=link_colors,
        ),
        textfont=dict(color="white", size=20)
    ))

   

    fig.update_layout(
        height=1000,
    )

    return fig
    