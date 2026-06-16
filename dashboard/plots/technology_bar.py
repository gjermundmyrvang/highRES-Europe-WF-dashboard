import plotly.express as px

def plot_tot_bars(df):
    fig = px.bar(
        df,
        x="g",
        y=["existing", "value_new"],
        labels={"g": "Technology", "value": "Capacity (GW)", "variable": "Type"},
        height=700,
        width=900
    )
    return fig
