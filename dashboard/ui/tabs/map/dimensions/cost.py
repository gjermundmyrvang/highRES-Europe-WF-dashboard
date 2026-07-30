import streamlit as st

from data.transformer import random_hex_color
from data.constants import COST_COMPONENTS
from data.cost_transformer import get_category_totals_by_zone
from .base import MapDimensionResult

LABEL = "Cost"


def render_controls(data, selected, inflation_factor, rate) -> MapDimensionResult:
    disable_dropdown = selected is not None

    with st.container(border=True):
        category = st.selectbox(
            "Cost category",
            options=list(COST_COMPONENTS.keys()),
            disabled=disable_dropdown,
        )

    agg = get_category_totals_by_zone(data, category, inflation_factor, rate)
    color = random_hex_color(category)

    # NOTE: "Transmission" cost is cross-zone; per-zone attribution here uses
    # the same naive filter as elsewhere in the app. See TODO in
    # cost_transformer.generate_total_category_breakdown().

    return MapDimensionResult(df=agg, legend_label=f"{category} Cost", color=color)
