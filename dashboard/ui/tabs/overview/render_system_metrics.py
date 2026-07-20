import streamlit as st
from data.cost_transformer import (
    adjust_currency,
    adjust_inflation,
    get_exchange_rate,
    get_currencies,
    format_money,
)
from data_loader import scalar, table
from ..shared.key_data import render_key_data
from data.constants import COST_COMPONENTS, get_country_name


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

    # List of included countries
    _render_countries(sets)

    st.divider()

    # Capacity Overview
    st.subheader("Installed Capacity")
    render_key_data(data, sets)

    st.divider()

    total_col, breakdown_col = st.columns([0.3, 0.7], gap="large")
    with total_col:
        # Total Cost
        st.subheader("Costs")
        inflation_factor, selected_currency = _render_cost_settings()

        total_cost = data["costs"].iloc[0]["value"]
        gbp_value = total_cost * 1_000_000
        adjusted_gbp = adjust_inflation(gbp_value, inflation_factor)
        rate, is_offline = get_exchange_rate(selected_currency["iso_code"])
        adjusted = format_money(adjust_currency(adjusted_gbp, rate))

        # Handle if user does not have internet connection
        if is_offline:
            st.warning("No internet connection, live exchange rates unavailable.")
            rate = st.number_input(
                "Enter exchange rate manually (GBP → selected currency)",
                min_value=0.01,
                value=1.0,
                step=0.01,
            )

        with st.container(border=True):
            delta_str = (
                f"Manual rate at {rate:.4f}"
                if is_offline
                else f"{selected_currency['iso_code']} at {rate:.4f}"
            )
            st.metric(
                ":material/payments: &nbsp; **Total System Cost**",
                f"{selected_currency['symbol']}{adjusted}",
                delta=f"×{inflation_factor} inflation | {delta_str}",
            )
            st.caption(f"Raw model output: £{format_money(gbp_value)} (2010 GBP)")
            # Cost per MWh in selected currency
            demand_df = data["demand"]
            total_demand_gwh = demand_df["value"].sum()
            cost_per_mwh = adjust_currency(adjusted_gbp, rate) / (
                total_demand_gwh * 1000
            )
            st.metric(
                "**System Average Cost**",
                f"{cost_per_mwh:.2f} {selected_currency['iso_code']}/MWh",
            )

    with breakdown_col:
        # Cost breakdown
        category = st.segmented_control(
            "Cost breakdown",
            options=["Generation", "Storage", "Transmission"],
            default=None,
        )

        if category:
            _render_cost_breakdown(
                data, category, inflation_factor, rate, selected_currency, gbp_value
            )
        else:
            st.caption("Select a category above to see the breakdown.")

    return inflation_factor, selected_currency, rate


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
    df_names = df.map(get_country_name)

    with st.expander(
        f":material/public: &nbsp; {len(df)} countries included in this scenario"
    ):
        st.dataframe(df_names, hide_index=True)


def _render_cost_breakdown(
    data, category, inflation_factor, rate, selected_currency, gbp_value
):
    components = COST_COMPONENTS[category]
    symbol = selected_currency["symbol"]

    # Sum all component values and convert from millions to full value
    category_total_gbp = (
        sum(
            data[var]["value"].sum()
            for var in components
            if var in data and not data[var].empty
        )
        * 1_000_000
    )

    # Adjust for inflation and convert to selected currency
    category_total_adjusted_gbp = adjust_inflation(category_total_gbp, inflation_factor)
    category_total_converted = adjust_currency(category_total_adjusted_gbp, rate)
    category_total_formatted = format_money(category_total_converted)
    category_pct = (category_total_gbp / gbp_value * 100).round(1)

    st.metric(
        f":material/payments: **{category} Total**",
        f"{symbol}{category_total_formatted}",
        delta=f"{category_pct}% of total system cost",
    )

    shown_components = {}
    not_shown = set()

    for key, value in components.items():
        if key not in data or data[key].empty:
            not_shown.add(key)
        else:
            shown_components[key] = value

    num_cols = 4
    cols = st.columns(num_cols, gap="large")
    for i, var in enumerate(shown_components):
        # Get raw value in GBP millions and convert to full value
        raw_gbp = data[var]["value"].sum() * 1_000_000

        # Adjust for inflation and convert to selected currency
        adjusted_gbp = adjust_inflation(raw_gbp, inflation_factor)
        converted = adjust_currency(adjusted_gbp, rate)
        formatted = format_money(converted)

        cols[i % num_cols].metric(var, f"{symbol}{formatted}", border=True)

    if not_shown:
        st.info(f"Not shown (not included in scenario): {', '.join(sorted(not_shown))}")
