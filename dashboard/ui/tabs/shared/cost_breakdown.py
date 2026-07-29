import streamlit as st
from data.cost_transformer import (
    generate_total_category_breakdown,
)


def render_cost_breakdown(
    data,
    category,
    inflation_factor,
    rate,
    selected_currency,
    gbp_value,
    selected_country=None,
):
    """
    IMPORTANT:
    ----------
    If a zone is passed (`selected_country is not None`), the "Transmission"
    category needs revising: transmission costs represent energy
    transfer *between* zones, so naive per-zone filtering doesn't
    correctly attribute them to a single country.
    See TODO in `generate_total_category_breakdown()` for details.
    """

    total_breakdown = generate_total_category_breakdown(
        data, inflation_factor, rate, category, selected_country
    )
    symbol = selected_currency["symbol"]

    category_pct = (total_breakdown["category_total_gbp"] / gbp_value * 100).round(1)

    st.metric(
        f":material/payments: **{category} Total**",
        f"{symbol}{total_breakdown['category_total_formatted']}",
        delta=f"{category_pct}% of total system cost",
    )

    num_cols = 4
    cols = st.columns(num_cols, gap="large")
    for i, var in enumerate(total_breakdown["shown"]):
        cols[i % num_cols].metric(
            var["name"], f"{symbol}{var['formatted']}", border=True
        )

    not_shown_items = total_breakdown["not_shown"]
    if len(not_shown_items) > 0:
        not_shown_str = ", ".join(not_shown_items)
        st.info(title="Not shown (not included in gdx):", body=not_shown_str)
