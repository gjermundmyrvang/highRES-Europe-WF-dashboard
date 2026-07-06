import streamlit as st
from data.cost_transformer import (
    adjust_currency,
    adjust_inflation,
    get_exchange_rate,
    get_currencies,
    format_money,
)
from data_loader import scalar, table
from ..shared import render_key_data


def render_system_metrics(data, sets):

    # Scenario details
    day = int(scalar(sets, "day"))
    month = int(scalar(sets, "month"))
    year = int(scalar(sets, "year"))

    hfirst = int(scalar(sets, "hfirst"))
    hlast = int(scalar(sets, "hlast")) + 1
    resolution = (hlast - hfirst) / 8760

    st.markdown(f":material/calendar_month: &nbsp; **{day:02d}/{month:02d}/{year}**")
    st.markdown(f":material/schedule: &nbsp; **{resolution:.1f} year** resolution")
    st.markdown(f":material/timer: &nbsp; Hours **{hfirst}–{hlast - 1}**")

    st.divider()

    # Capacity Overview
    st.subheader("Installed Capacity")
    render_key_data(data)

    st.divider()

    # HERO: Total Cost
    st.subheader("Cost")
    inflation_factor, selected_currency = _render_cost_settings()

    total_cost = data["costs"].iloc[0]["value"]
    gbp_value = total_cost * 1_000_000
    adjusted_gbp = adjust_inflation(gbp_value, inflation_factor)
    rate = get_exchange_rate(selected_currency["iso_code"])
    adjusted = format_money(adjust_currency(adjusted_gbp, rate))

    with st.container(border=True):
        st.metric(
            ":material/payments: &nbsp; **Total System Cost**",
            f"{selected_currency['symbol']}{adjusted}",
            delta=f"×{inflation_factor} inflation · {selected_currency['iso_code']} at {rate:.4f}",
        )
        st.caption(f"Raw model output: £{format_money(gbp_value)} (2010 GBP)")

    # List of included countries
    _render_countries(sets)


def _render_cost_settings():
    with st.popover(":material/settings: Cost settings"):
        inflation_factor = st.number_input(
            "Inflation factor (2010 → today)",
            min_value=0.5,
            max_value=6.0,
            value=1.589,
            step=0.05,
            help="Source: Bank of England inflation calculator",
        )
        currencies = get_currencies()
        currency_options = {f"{c['name']} ({c['iso_code']})": c for c in currencies}
        default_index = list(currency_options.keys()).index("Euro (EUR)")
        selected_label = st.selectbox(
            "Display currency",
            options=list(currency_options.keys()),
            index=default_index,
        )

    return inflation_factor, currency_options[selected_label]


def _render_countries(sets):
    countries = table(sets, "z")
    df = countries[["*"]].rename(columns={"*": "Country"})

    with st.expander(
        f":material/public: &nbsp; {len(df)} countries included in this scenario"
    ):
        st.dataframe(df, hide_index=True)
