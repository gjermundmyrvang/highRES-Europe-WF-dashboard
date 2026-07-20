import gdxpds
import pandas as pd
from pathlib import Path
import yaml
from data.constants import get_country_name

VARIABLES = [
    "var_tot_pcap",
    "var_tot_pcap_z",
    "var_new_pcap",
    "var_new_pcap_z",
    "var_new_vre_pcap_r",
    "var_tot_trans_pcap",
    "costs",
    "costs_gen_capex",
    "costs_gen_fom",
    "costs_gen_varom",
    "costs_gen_start",
    "costs_gen_vreconnection",
    "costs_store_capex",
    "costs_store_fom",
    "costs_store_varom",
    "costs_store_start",
    "costs_trans_capex",
    "costs_trans_fom",
    "area",
]

SETS = ["hfirst", "hlast", "day", "month", "year", "vre", "z"]

THRESHOLD = 1e-3  # Store only levels (values) > 0.001


def load_config():
    config_path = Path("dashboard/dashboard_config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {
        "results_path": "work_test",
        "geojson_path": "intermediate_data/region/shapes/europe_onshore.geojson",
    }


def load_standard_scenarios(base_path: str | Path) -> dict[str, Path]:
    # Looks for model-generated scenarios: base_path/scenario_name/results.gdx
    base_path = Path(base_path)
    return {gdx.parent.name: gdx for gdx in sorted(base_path.glob("*/results.gdx"))}


def load_custom_scenarios(folder_path: str | Path) -> dict[str, Path]:
    # Looks for flat GDX files: folder_path/scenario_name.gdx
    folder_path = Path(folder_path)
    return {gdx.stem: gdx for gdx in sorted(folder_path.glob("*.gdx"))}


def load_results(
    gdx_path: str | Path, gams_path: str | Path
) -> dict[str, pd.DataFrame]:
    gdx_path = Path(gdx_path)
    if not gdx_path.exists():
        raise FileNotFoundError(f"No GDX file found at {gdx_path}")

    results = {}
    with gdxpds.gdx.GdxFile(lazy_load=True, gams_dir=str(gams_path)) as gdx:
        gdx.read(str(gdx_path))
        for var in VARIABLES:
            if var in gdx:
                gdx[var].load()
                results[var] = gdx[var].dataframe.copy()
            else:
                print(f"Warning: {var} not found in {gdx_path.name}")

    return results


def clean_results(results: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    cleaned = {}
    for name, df in results.items():
        df = df.rename(columns={"vre": "g"})
        dims = [
            c for c in df.columns if c in ("g", "r", "z", "z_alias", "trans", "vre")
        ]
        value_col = next(c for c in df.columns if c.lower() in ("level", "value"))
        cleaned[name] = (
            df[dims + [value_col]]
            .rename(columns={value_col: "value"})
            .query("value > @THRESHOLD")
            .reset_index(drop=True)
        )
        if "z" in cleaned[name].columns:
            cleaned[name]["country_name"] = cleaned[name]["z"].apply(get_country_name)
    return cleaned


def load_sets(gdx_path: str | Path, gams_path: str | Path) -> dict:
    gdx_path = Path(gdx_path)
    sets = {}

    with gdxpds.gdx.GdxFile(lazy_load=True, gams_dir=str(gams_path)) as gdx:
        gdx.read(str(gdx_path))

        for s in SETS:
            if s not in gdx:
                continue

            gdx[s].load()
            df = gdx[s].dataframe.copy().reset_index(drop=True)

            # need to seperate different types of sets
            if df.shape[0] == 1 and len(df.columns) >= 1:
                sets[s] = {"type": "scalar", "value": df.iloc[0, 0]}
            else:
                sets[s] = {"type": "table", "data": df}

    return sets


def scalar(sets, key):
    return sets[key]["value"]


def table(sets, key):
    return sets[key]["data"]
