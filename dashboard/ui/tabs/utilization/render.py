import streamlit as st
import numpy as np
from data.utilization import (
    calculate_utilization,
    calculate_utilization_region,
    calculate_country_land_use,
)
from data.constants import get_capacity_to_area
from . import (
    render_utilization_header,
    render_vre_summary,
    render_breakdown,
    render_land_usage,
)


def render_utilization(df, country_areas):
    st.title("Renewable Energy Deployment")
    # Header
    unit, use_area, show_land_pct, unit_label = render_utilization_header()

    # Data preparation
    potential_z = df["area"].replace([np.inf, -np.inf], np.nan)
    new_vre_z = df["var_new_vre_pcap_r"]

    # cap2area dict
    cap2area = get_capacity_to_area(df)

    util_df = calculate_utilization(new_vre_z, potential_z, cap2area, use_area=use_area)

    total_installed = util_df["installed"].sum().round(1)
    total_potential = util_df["potential"].sum().round(1)
    util_pct = (total_installed / total_potential * 100).round(1)
    util_pct = float(util_pct) if not np.isnan(util_pct) else 0.0

    # LAND USAGE
    if show_land_pct:
        _render_land_util(potential_z, new_vre_z, cap2area, use_area, country_areas)

    else:
        # VRE aggregated
        render_vre_summary(
            util_df, total_installed, total_potential, util_pct, unit_label, unit
        )

        # By technology + by country + by both
        render_breakdown(util_df, unit_label)


def _render_land_util(potential_z, new_vre_z, cap2area, use_area, country_areas):
    # Exclude Windoffshore technologies
    potential_z_land = potential_z[
        ~potential_z["g"].str.startswith("Windoff", na=False)
    ]
    new_vre_z_land = new_vre_z[~new_vre_z["g"].str.startswith("Windoff", na=False)]

    util_df = calculate_utilization(
        new_vre_z_land, potential_z_land, cap2area, use_area=use_area
    )
    util_region_df = calculate_utilization_region(
        new_vre_z_land, potential_z_land, cap2area, use_area=use_area
    )

    total_installed = util_df["installed"].sum().round(1)
    total_potential = util_df["potential"].sum().round(1)
    util_pct = (total_installed / total_potential * 100).round(1)
    util_pct = float(util_pct) if not np.isnan(util_pct) else 0.0

    land_df = calculate_country_land_use(
        new_vre_z_land, potential_z_land, country_areas, cap2area
    )
    render_land_usage(land_df, util_df, util_region_df)
