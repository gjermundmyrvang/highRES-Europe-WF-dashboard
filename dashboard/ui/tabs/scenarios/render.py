from __future__ import annotations
import random

import pandas as pd
import plotly.express as px
import streamlit as st

from data.constants import TECH_COLORS
from data.loader import load_scenario_summary
from data.cost_transformer import format_money

SCALAR_METRICS = {
    ("capacity", "total_installed"): "Total Capacity (GW)",
    ("capacity", "new_installed"): "New Capacity (GW)",
    ("vre", "total_vre"): "Total VRE (GW)",
    ("vre", "new_vre"): "New VRE (GW)",
    ("storage", "tot_storage"): "Total Storage (GW)",
    ("cost", "cost_raw"): "Total System Cost",
    ("demand", "by_demand"): "Normalized by Demand",
}


def scenario_to_tidy(summary: dict, scenario_name: str) -> pd.DataFrame:
    """Turn one scenario's summary dict into tidy rows.

    Each row is: (scenario, category, dimension, item, value).
    "dimension" is empty for plain scalar metrics, and holds the breakdown
    type ("technology", "cost_component", etc.) for breakdown rows.

    To wire in a new GDX table, add a loop here that appends rows in the
    same shape --> the rest of the app (tables, charts) will pick it up
    automatically.
    """
    rows = []

    for (category, key), label in SCALAR_METRICS.items():
        if key in summary:
            value = summary[key]
            rows.append((scenario_name, category, "", label, value))

    for tech, value in summary.get("tech_breakdown", {}).items():
        rows.append(
            (scenario_name, "category_mix", "new installed capacity (GW)", tech, value)
        )

    for tech, value in summary.get("vre_breakdown", {}).items():
        rows.append(
            (
                scenario_name,
                "category_mix",
                "new installed renewable capacity (GW)",
                tech,
                value,
            )
        )

    for tech, value in summary.get("storage_breakdown", {}).items():
        rows.append((scenario_name, "category_mix", "storages (GW)", tech, value))

    for component, value in summary.get("cost_breakdown", {}).items():
        rows.append((scenario_name, "category_mix", "costs", component, value))

    columns = ["scenario", "category", "dimension", "item", "value"]
    return pd.DataFrame(rows, columns=columns)


# Combine every scenario's tidy rows into one big dataframe.
def build_tidy(summaries: dict[str, dict | None]) -> pd.DataFrame:
    columns = ["scenario", "category", "dimension", "item", "value"]
    frames = []

    for scenario_name, summary in summaries.items():
        if summary is None:
            continue
        frames.append(scenario_to_tidy(summary, scenario_name))

    if not frames:
        return pd.DataFrame(columns=columns)

    return pd.concat(frames, ignore_index=True)


# Returns (values, deltas). `deltas` is None when there's no base
# scenario to compare against.
def wide_with_delta(
    tidy: pd.DataFrame, base_scenario: str | None
) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    scalar_rows = tidy[tidy["dimension"] == ""]
    values = scalar_rows.pivot_table(
        index="scenario", columns="item", values="value", aggfunc="first"
    )

    deltas = None
    if base_scenario is not None and base_scenario in values.index:
        base_row = values.loc[base_scenario]
        deltas = values.subtract(base_row, axis=1)

    return values, deltas


def format_metric_value(value: float, column_name: str, selected_currency) -> str:
    if pd.isna(value):
        return "\u2014"  # em dash, for missing values

    is_cost_column = "cost" in column_name.lower()
    if is_cost_column:
        return format_money(value)

    is_demand_column = "demand" in column_name.lower()
    if is_demand_column:
        return f"{value:,.1f} {selected_currency['iso_code']}/MWh"
    return f"{value:,.1f}"


# creates cells that becomes something like "123.4" or "123.4 (\u0394 +5.0)" for
# non-base scenarios when a base scenario is selected.
def build_display_table(
    values: pd.DataFrame,
    deltas: pd.DataFrame | None,
    base_scenario: str | None,
    selected_currency,
) -> pd.DataFrame:
    display_values = pd.DataFrame(
        index=values.index, columns=values.columns, dtype=object
    )

    for scenario in values.index:
        for column in values.columns:
            raw_value = values.loc[scenario, column]
            text = format_metric_value(raw_value, column, selected_currency)

            show_delta = deltas is not None and scenario != base_scenario
            if show_delta:
                delta_value = deltas.loc[scenario, column]
                delta_text = format_metric_value(delta_value, column, selected_currency)
                # format_metric_value doesn't add a "+" sign, so add one here
                if not pd.isna(delta_value) and delta_value >= 0:
                    delta_text = f"+{delta_text}"
                text = f"{text} (\u0394 {delta_text})"

            display_values.loc[scenario, column] = text

    return display_values


# SUMMARY DATAFRAME
def render_summary_table(
    values: pd.DataFrame,
    deltas: pd.DataFrame | None,
    base_scenario: str | None,
    highlight: str,
    selected_currency,
):
    display_values = build_display_table(
        values, deltas, base_scenario, selected_currency
    )

    styler = values.style
    for scenario in values.index:
        for column in values.columns:
            text = display_values.loc[scenario, column]
            cell = pd.IndexSlice[[scenario], [column]]
            styler = styler.format(lambda _, text=text: text, subset=cell)

    if highlight == "Max":
        styler = styler.highlight_max(axis=0)
    elif highlight == "Min":
        styler = styler.highlight_min(axis=0)

    st.dataframe(styler)


def get_technology_order(
    mix_rows: pd.DataFrame, base_scenario: str | None
) -> list[str]:
    if base_scenario in mix_rows["scenario"].values:
        rows_to_use = mix_rows[mix_rows["scenario"] == base_scenario]
    else:
        rows_to_use = mix_rows

    totals_by_tech = rows_to_use.groupby("item")["value"].sum()
    ordered_techs = totals_by_tech.sort_values(ascending=False).index.tolist()
    return ordered_techs


def _random_hex_color(seed_str):
    """
    TODO:
    -----
    This is used in `render_capacity_mix` so dimensions with other 'techs' thats does not have a color dict also gets a unique color. However random hex can produce colors that are too dark, too light, or low-contrast against the dashboard background. A better solution should be implemented.
    """
    rng = random.Random(seed_str)
    return "#{:06x}".format(rng.randint(0, 0xFFFFFF))


# CAPACITY MIX (one bar per scenario, one segment per technology/category)
def render_category_mix(tidy: pd.DataFrame, base_scenario: str | None):

    mix_rows = tidy[tidy["category"] == "category_mix"]
    if mix_rows.empty:
        st.info("No mix data available.")
        return

    # Select which mix to display (e.g. new VRE capacity, storage, costs)
    available_dimensions = sorted(mix_rows["dimension"].unique())
    selected_dimension = st.selectbox(
        "Mix type",
        available_dimensions,
        format_func=lambda d: d.replace("_", " ").title(),
    )

    dimension_rows = mix_rows[mix_rows["dimension"] == selected_dimension]

    plot_data = dimension_rows.copy()

    unit = st.radio(
        "Show as", ["Absolute (GW)", "Share of total (%)"], horizontal=True, index=0
    )
    if unit == "Share of total (%)":
        totals_per_scenario = plot_data.groupby("scenario")["value"].transform("sum")
        plot_data["plot_value"] = 100 * plot_data["value"] / totals_per_scenario
        y_axis_label = "Share of total (%)"
    else:
        plot_data["plot_value"] = plot_data["value"]
        y_axis_label = selected_dimension.replace("_", " ").title()

    tech_order = get_technology_order(plot_data, base_scenario)
    tech_colors = {
        tech: TECH_COLORS.get(tech, _random_hex_color(tech))
        for tech in plot_data["item"].unique()
    }

    fig = px.bar(
        plot_data,
        x="scenario",
        y="plot_value",
        color="item",
        category_orders={"item": tech_order},
        color_discrete_map=tech_colors,
        labels={
            "plot_value": y_axis_label,
            "item": "Category",
            "scenario": "Scenario",
        },
    )
    fig.update_layout(barmode="stack", legend_title_text="Technology")
    fig.update_traces(marker_line_width=0)

    if base_scenario:
        scenario_names = plot_data["scenario"].unique()
        for position, scenario in enumerate(scenario_names):
            if scenario == base_scenario:
                # Draw a box around the base scenario's bar so it's easy to spot.
                fig.add_vrect(
                    x0=position - 0.4,
                    x1=position + 0.4,
                    line_width=2,
                    line_color="#F5A623",
                    fillcolor="rgba(0,0,0,0)",
                )

    st.plotly_chart(fig)


# BREAKDOWN CHART (e.g: generation costs across scenarios)
def render_breakdown_chart(tidy: pd.DataFrame, base_scenario: str | None):
    breakdown_rows = tidy[tidy["dimension"] != ""]
    if breakdown_rows.empty:
        st.info("No breakdown data available for the selected scenarios.")
        return

    # Select dimension (e.g costs or technologies)
    available_dimensions = sorted(breakdown_rows["dimension"].unique())
    selected_dimension = st.selectbox(
        "Breakdown by",
        available_dimensions,
        format_func=lambda d: d.replace("_", " ").title(),
    )

    dimension_rows = breakdown_rows[breakdown_rows["dimension"] == selected_dimension]

    # Select type (e.g technologies/Solar)
    available_items = sorted(dimension_rows["item"].unique())
    selected_item = st.selectbox("Item", available_items)

    item_rows = dimension_rows[dimension_rows["item"] == selected_item]
    value_by_scenario = item_rows.groupby("scenario")["value"].first()

    base_value = None
    if base_scenario is not None:
        base_value = value_by_scenario.get(base_scenario)

    chart_data = value_by_scenario.reset_index()
    chart_data["is_base"] = chart_data["scenario"] == base_scenario

    if base_value is not None:
        chart_data["delta"] = chart_data["value"] - base_value
    else:
        chart_data["delta"] = float("nan")

    chart_data = chart_data.sort_values("value", ascending=True)

    bar_colors = {True: "#F5A623", False: TECH_COLORS.get(selected_item, "#1B5FA8")}

    fig = px.bar(
        chart_data,
        x="value",
        y="scenario",
        orientation="h",
        color="is_base",
        color_discrete_map=bar_colors,
        custom_data=["delta"],
        height=max(300, len(chart_data) * 40),
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Value: %{x:,.1f}<br>"
            "\u0394 vs base: %{customdata[0]:+,.1f}<extra></extra>"
        )
    )
    fig.update_layout(showlegend=False, xaxis_title=selected_item)

    if base_value is not None:
        fig.add_vline(
            x=base_value,
            line_dash="dash",
            line_color="#F5A623",
            annotation_text="Base",
        )

    st.plotly_chart(fig)


# LOAD ALL SCENARIOS (calls `load_scenario_summary` for each scenario and caches data)
def load_all_summaries(
    visible_scenarios: dict, config, inflation_factor, rate
) -> dict[str, dict | None]:
    summaries = {}
    total = len(visible_scenarios)
    progress_bar = st.progress(0, text="Loading scenarios...")

    gams_path = config.get("gams_path")
    variables = config.get("variables")
    user_sets = config.get("sets")

    for i, (name, gdx_path) in enumerate(visible_scenarios.items(), start=1):
        progress_bar.progress(i / total, text=f"Loading '{name}' ({i}/{total})...")
        try:
            summaries[name] = load_scenario_summary(
                str(gdx_path), gams_path, variables, user_sets, inflation_factor, rate
            )
        except Exception as exc:
            summaries[name] = None
            st.warning(f"Could not load '{name}': {exc}")

    progress_bar.empty()
    return summaries


# RENDER (top level render function orchistrator)
def render_scenarios(
    all_scenarios: dict, config, inflation_factor, selected_currency, rate
):
    st.title("Scenarios Overview")

    selected_names = st.multiselect(
        "Select scenarios to compare",
        options=list(all_scenarios.keys()),
        default=list(all_scenarios.keys()),
    )
    visible_scenarios = {
        name: path for name, path in all_scenarios.items() if name in selected_names
    }

    base_scenario_choice = st.selectbox(
        "Base scenario (compare all others against this)",
        options=["None"] + list(visible_scenarios.keys()),
        index=0,
    )
    base_scenario = None if base_scenario_choice == "None" else base_scenario_choice

    summaries = load_all_summaries(visible_scenarios, config, inflation_factor, rate)
    tidy = build_tidy(summaries)

    st.header("Summary Table")
    highlight = st.radio("Highlight", ["Max", "Min", "None"], horizontal=True, index=2)
    values, deltas = wide_with_delta(tidy, base_scenario)
    render_summary_table(values, deltas, base_scenario, highlight, selected_currency)

    st.divider()
    st.subheader("Category Mix by Scenario")  # TODO: Better label?
    render_category_mix(tidy, base_scenario)

    st.divider()
    st.subheader("Breakdown Comparison Across Scenarios")
    render_breakdown_chart(tidy, base_scenario)
