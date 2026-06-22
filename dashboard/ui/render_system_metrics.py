import streamlit as st
from data.cost_transformer import adjust_currency, adjust_inflation, get_eur_gbp_rate

def render_system_metrics(data):
    inflation_factor = st.number_input(
        "Inflation adjustment factor",
        min_value=0.5,
        max_value=6.0,
        value=1.30,   # assumption
        step=0.05,
        help="Multiplier applied to convert historical GBP into today's GBP",
        width=300
    )

    total_cost = data["costs"].iloc[0]["value"]
    gbp_value = total_cost * 1_000_000
    adjusted_gbp = adjust_inflation(gbp_value, inflation_factor)
    adjusted_eur = adjust_currency(adjusted_gbp, get_eur_gbp_rate())

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Model Raw Cost",
            f"£{round(gbp_value):,}",
            delta_description="Year: 2010"
        )

    with col2:
        st.metric(
            "Adjusted Cost Today",
            f"€{adjusted_eur:,.0f}",
        )

    st.info(
        "Cost adjusted for inflation and converted from GBP to EUR."
    )