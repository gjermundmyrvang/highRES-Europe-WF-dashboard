from dataclasses import dataclass
import pandas as pd


@dataclass
class MapDimensionResult:
    """
    The common shape every map dimension must produce.

    df: must contain columns ["z", "country_name", "value"], one row per zone.
    legend_label: shown as the colorbar/legend title, e.g. "GW", "£M".
    color: hex color used to build the choropleth's color scale.
    """

    df: pd.DataFrame
    legend_label: str
    color: str
