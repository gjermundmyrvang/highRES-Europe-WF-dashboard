import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data.country_names import get_country_name

TECH_COLORS = {
    "Solar":               "#F5C518",
    "Windonshore":         "#4A90D9",
    "Windoffshore":        "#1B5FA8",
    "WindoffshoreFloat":   "#0D3B6E",
    "HydroRoR":            "#2ECC71",
    "HydroRes":            "#1A8C4E",
    "NuclearEPR":          "#E74C3C",
}

DEFAULT_COLOR = "#cccccc"

def plot_capacity_pies(df, cols: int = 4):
    countries = sorted(set(df["z"]))
    n = len(countries)
    rows = -(-n // cols)

    fig = make_subplots(
        rows=rows, cols=cols,
        specs=[[{"type": "pie"}] * cols for _ in range(rows)],
        subplot_titles=[get_country_name(c) for c in countries],
    )

    for i, country in enumerate(countries):
        row = i // cols + 1
        col = i %  cols + 1
 
        sub = df[df["z"] == country].sort_values("value", ascending=False)
        colors = [TECH_COLORS.get(t, DEFAULT_COLOR) for t in sub["g"]]
 
        fig.add_trace(
            go.Pie(
                labels=sub["g"],
                values=sub["value"],
                name=country,
                marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0.3)", width=1)),
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>%{value:.3f} GW<br>%{percent}<extra></extra>",
                showlegend=True,
                legendgroup="techs",   
            ),
            row=row, col=col,
        )
 
    fig.update_layout(
        height=max(350 * rows, 400),
        legend=dict(
            orientation="v",
            x=1.01, y=1,
            title_text="Technology",
            font=dict(size=11),
        ),
    )
 
    for annotation in fig.layout.annotations:
        annotation.font = dict(color="black", size=16)
 
    return fig