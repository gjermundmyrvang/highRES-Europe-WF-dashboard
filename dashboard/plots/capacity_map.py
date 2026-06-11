import plotly.express as px

def plot_zone_map(df, geo, value_col):
    fig = px.choropleth(
        df,
        geojson=geo,
        locations="z",
        featureidkey="properties.index",
        color=value_col,
        color_continuous_scale="Blues",
        height=700
    )
    fig.update_geos(fitbounds="locations", visible=False)
    return fig