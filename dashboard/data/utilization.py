import numpy as np

# TODO: This is different between techs?
AREA_FACTOR = 2.4  # 1 km² produces 2.4 GW?


def calculate_utilization(tot_z, potential_z):
    vre_techs = set(potential_z["g"].unique()) # area-table only has VRE techs
    installed_vre = tot_z[tot_z["g"].isin(vre_techs)]
 
    installed_agg = (
        installed_vre
        .groupby(["z", "g"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "installed"}) # For code clarity later on
    )
 
    potential_agg = (
        potential_z
        .groupby(["z", "g"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "potential"}) # For code clarity later on
    )
 
    df = potential_agg.merge(installed_agg, on=["z", "g"], how="left")
    df["installed"] = df["installed"].fillna(0)
 
    # If potential > 0, calculate utilization as installed/potential * 100. Otherwise set it to NaN
    df["utilization_pct"] = np.where(
        df["potential"] > 0,
        df["installed"] / df["potential"] * 100,
        np.nan,
    )
 
    return df


def calculate_area_utilization(df):
    df["potential_area"] = df["potential"] / AREA_FACTOR
    df["installed_area"] = df["installed"] / AREA_FACTOR
    df["unused_area"] = df["potential_area"] - df["installed_area"]

    country_area = df.groupby("z").agg(
    potential_area=("potential_area", "sum"),
    installed_area=("installed_area", "sum"),
    ).reset_index()

    country_area["utilization_pct"] = (
        country_area["installed_area"] / country_area["potential_area"] * 100
    )
    return country_area
    