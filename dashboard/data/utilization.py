import numpy as np
from data.constants import COUNTRY_AREA_KM2
from data.country_names import get_country_name

# TODO: This is different between techs?
AREA_FACTOR = 2.4  # 1 km² produces 2.4 GW?

CAPACITY_TO_AREA = {
    "Solar": 0.04,
    "Windoffshore": 0.005,
    "Windonshore": 0.0024,
    "HydroRoR": 0.001,
}


def calculate_utilization(new_vre_z, potential_z, use_area=False):
    potential_z = potential_z[potential_z["g"] != "HydroRoR"]  # Exclude (INF+)
    vre_techs = set(potential_z["g"].unique())  # area-table only has VRE techs
    installed_vre = new_vre_z[new_vre_z["g"].isin(vre_techs)]

    installed_agg = (
        installed_vre.groupby(["z", "g"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "installed"})  # For code clarity later on
    )

    potential_agg = (
        potential_z.groupby(["z", "g"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "potential"})  # For code clarity later on
    )

    df = potential_agg.merge(installed_agg, on=["z", "g"], how="left")
    df["installed"] = df["installed"].fillna(0)

    if use_area:
        df["installed"] = df["installed"] / df["g"].map(CAPACITY_TO_AREA)
        df["potential"] = df["potential"] / df["g"].map(CAPACITY_TO_AREA)

    # If potential > 0, calculate utilization as installed/potential * 100. Otherwise set it to NaN
    df["utilization_pct"] = np.where(
        df["potential"] > 0,
        (df["installed"] / df["potential"] * 100),
        np.nan,
    )
    df["country_name"] = df["z"].apply(get_country_name)
    return df


def calculate_country_land_use(new_vre_z, potential_z):
    # Calculates installed VRE area as % of total country land area
    util_df = calculate_utilization(new_vre_z, potential_z, use_area=False)

    # Convert installed GW to km²
    util_df["installed_area"] = util_df["installed"] / util_df["g"].map(
        CAPACITY_TO_AREA
    )
    util_df["potential_area"] = util_df["potential"] / util_df["g"].map(
        CAPACITY_TO_AREA
    )

    # Aggregate to country level
    country_df = (
        util_df.groupby("z")[["installed_area", "potential_area"]].sum().reset_index()
    )
    country_df["country_area_km2"] = country_df["z"].map(COUNTRY_AREA_KM2)
    country_df["remaining_potential"] = (
        country_df["potential_area"] - country_df["installed_area"]
    )
    country_df["remaining_country"] = (
        country_df["country_area_km2"] - country_df["potential_area"]
    )
    country_df["land_use_pct"] = (
        country_df["installed_area"] / country_df["country_area_km2"] * 100
    ).round(2)

    country_df["country_name"] = country_df["z"].apply(get_country_name)
    return country_df


def aggregate_potential(df):
    df = df[df["g"] != "HydroRoR"]
    return df.groupby(["g"], as_index=False)["value"].sum()


def capacity_to_area(df):
    df = df.copy()

    df["factor"] = df["g"].map(CAPACITY_TO_AREA)
    df = df.dropna(subset=["factor"])

    df["area_km2"] = df["value"] * df["factor"]

    return df
