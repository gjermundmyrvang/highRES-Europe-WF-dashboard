import plotly.express as px

def plot_tot_bars(df, view, value_col):
    fig = px.bar(
        df,
        x="g",
        y=value_col[view],
        labels={"g": "Technology", "value": "Capacity (GW)", "variable": "Type"},
        height=700,
    )
    return fig
