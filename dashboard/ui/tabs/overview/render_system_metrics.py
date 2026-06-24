import streamlit as st
from datetime import datetime, timedelta
from data.cost_transformer import adjust_currency, adjust_inflation, get_exchange_rate, get_currencies


def render_system_metrics(data, hour_data):
    # Hour Data
    _render_hour_data(hour_data)
    st.divider()

    st.subheader("Model Total Cost")
    # Settings 
    col_settings_1, col_settings_2 = st.columns([0.4, 0.6])

    with col_settings_1:
        inflation_factor = st.number_input(
            "Inflation adjustment factor",
            min_value=0.5,
            max_value=6.0,
            value=1.589,
            step=0.05,
            help="Multiplier to convert historical GBP into today's GBP. Source: Bank of England inflation calculator.",
        )

    with col_settings_2:
        currencies = get_currencies()
        currency_options = {f"{c['name']} ({c['iso_code']})": c for c in currencies}
        default_index = list(currency_options.keys()).index("Euro (EUR)")
        selected_label = st.selectbox(
            "Display currency",
            options=list(currency_options.keys()),
            index=default_index,
        )

    # Calculations 
    total_cost = data["costs"].iloc[0]["value"]
    gbp_value = total_cost * 1_000_000
    adjusted_gbp = adjust_inflation(gbp_value, inflation_factor)
    selected_currency = currency_options[selected_label]
    rate = get_exchange_rate(selected_currency["iso_code"])
    adjusted = adjust_currency(adjusted_gbp, rate)

    # Metrics
    col1, col2 = st.columns([0.4, 0.6], border=True)

    with col1:
        st.metric(
            "Model Raw Cost (2010)",
            f"£{gbp_value:,.0f}",
            delta=f"£{adjusted_gbp:,.0f} after inflation",
        )

    with col2:
        st.metric(
            "Adjusted Cost Today",
            f"{selected_currency['symbol']}{adjusted:,.0f}",
            delta=f"Converted from GBP to {selected_currency['iso_code']}",
        )

    st.caption(
        f"Raw model cost inflated by ×{inflation_factor} then converted from GBP to {selected_currency['iso_code']} at rate {rate:.4f}."
    )

def _render_hour_data(h_df):
    st.subheader("Model Metadata")
    
    st.metric("Scenario Created", f"{h_df['day']:02d}/{h_df['month']:02d}/{h_df['year']}")

    col1, col2 = st.columns(2)

    col1.metric("Model Time Range", f"Hour {h_df['hfirst']} --> Hour {h_df['hlast']}")
    col2.metric("Total Hours Modelled", h_df["hlast"] - h_df["hfirst"] + 1)