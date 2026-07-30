import requests
import streamlit as st
import pandas as pd

from data.constants import COST_COMPONENTS


@st.cache_data
def get_currencies():
    try:
        response = requests.get("https://api.frankfurter.dev/v2/currencies", timeout=5)
        return response.json()
    except Exception:
        return [{"iso_code": "EUR", "name": "Euro", "symbol": "€"}]


@st.cache_data
def get_exchange_rate(target_currency):
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v2/rates",
            params={"base": "GBP", "quotes": target_currency},
            timeout=5,
        )
        return response.json()[0]["rate"], False
    except Exception:
        return 1.0, True  # rate, user is offline


def adjust_inflation(gbp_value, factor):
    return gbp_value * factor


def adjust_currency(gbp_value, rate):
    adjusted = gbp_value * rate
    return adjusted


def format_money(value):
    abs_val = abs(value)

    if abs_val >= 1e12:
        return f"{value/1e12:.2f}T"
    if abs_val >= 1e9:
        return f"{value/1e9:.2f}B"
    if abs_val >= 1e6:
        return f"{value/1e6:.2f}M"

    return f"{value:,.0f}"


def _get_value(data, var, selected_country=None):
    if var not in data or data[var].empty:
        return None
    df = data[var]
    if selected_country:
        # NOTE: naive zone filter --> not valid for "Transmission" category,
        # see TODO in generate_total_category_breakdown().
        df = df[df["z"] == selected_country]
    return df["value"].sum()


# Returns tuple (gbp in millions, adjusted cost for inflation and currency)
# This is only for `costs` dataset
def get_total_costs_raw(data, inflation_factor, rate):
    total_cost = data["costs"].iloc[0]["value"]
    gbp_value = total_cost * 1_000_000
    adjusted_gbp = adjust_inflation(gbp_value, inflation_factor)
    adjusted_cost = adjust_currency(adjusted_gbp, rate)
    return gbp_value, adjusted_cost


# Returns tuple (gbp in millions, adjusted cost for inflation and currency)
# This is the different costs types, e.g `costs_gen_capex`
def get_total_cost_type(data, inflation_factor, rate, type, selected_country=None):
    raw_gbp = (_get_value(data, type, selected_country) or 0) * 1_000_000
    adjusted_gbp = adjust_inflation(raw_gbp, inflation_factor)
    converted = adjust_currency(adjusted_gbp, rate)
    return raw_gbp, converted


def generate_cost_breakdown(data, inflation_factor, rate, selected_country=None):
    cost_dict = {}
    for cost_type in COST_COMPONENTS.keys():
        components = COST_COMPONENTS[cost_type]
        category_total_gbp = (
            sum(
                v
                for var in components
                if (v := _get_value(data, var, selected_country)) is not None
            )
            * 1_000_000
        )
        category_total_adjusted_gbp = adjust_inflation(
            category_total_gbp, inflation_factor
        )
        category_total_converted = adjust_currency(category_total_adjusted_gbp, rate)
        cost_dict[cost_type] = category_total_converted
        cost_dict[f"{cost_type}_gbp"] = category_total_gbp

    return cost_dict


def generate_total_category_breakdown(
    data, inflation_factor, rate, category, selected_country=None
):
    """
    TODO: "Transmission" costs are inherently cross-zone
    (they represent energy transfer *between* countries), so attributing
    them to a single `selected_country` via simple filtering is probably not
    semantically correct because it doesn't distinguish import/export direction
    or split the cost sensibly between the two zones involved.
    This works fine for the overview tab (selected_country=None, i.e.
    totals across all zones), but needs real logic before it can be
    trusted in the country-detail view. Needs a decision on how
    transmission costs should be attributed/split per zone before this
    is relied upon downstream.
    """

    total_breakdown = {}

    breakdown_by_category = generate_cost_breakdown(
        data, inflation_factor, rate, selected_country
    )
    category_total = breakdown_by_category[category]
    category_total_gbp = breakdown_by_category[f"{category}_gbp"]

    total_breakdown["category_total"] = category_total
    total_breakdown["category_total_gbp"] = category_total_gbp
    total_breakdown["category_total_formatted"] = format_money(category_total)

    components = COST_COMPONENTS[category]
    shown_components = {}

    total_breakdown["not_shown"] = []

    for key, value in components.items():
        if key not in data or data[key].empty:
            total_breakdown["not_shown"].append(key)
        else:
            shown_components[key] = value

    total_breakdown["shown"] = []
    for cost_entry, _ in shown_components.items():
        raw_gbp, adjusted_cost = get_total_cost_type(
            data,
            inflation_factor,
            rate,
            type=cost_entry,
            selected_country=selected_country,
        )
        total_breakdown["shown"].append(
            {
                "name": cost_entry,
                "raw_gbp": raw_gbp,
                "adjusted_cost": adjusted_cost,
                "formatted": format_money(adjusted_cost),
            }
        )

    return total_breakdown


def get_category_totals_by_zone(data, category, inflation_factor, rate):
    """
    Per-zone version of generate_cost_breakdown: returns a DataFrame with
    one row per zone (z, country_name, value), where value is the summed,
    inflation- and currency-adjusted cost for the given category.

    Used by the map's Cost dimension, which needs values broken out per
    zone rather than a single total.
    """
    components = COST_COMPONENTS[category]
    frames = [
        data[var][["z", "country_name", "value"]]
        for var in components
        if var in data and not data[var].empty
    ]

    if not frames:
        return pd.DataFrame(columns=["z", "country_name", "value"])

    combined = pd.concat(frames)
    agg = combined.groupby(["z", "country_name"], as_index=False)["value"].sum()

    agg["value"] = agg["value"] * 1_000_000
    agg["value"] = adjust_inflation(agg["value"], inflation_factor)
    agg["value"] = adjust_currency(agg["value"], rate)

    return agg
