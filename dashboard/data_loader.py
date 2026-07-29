import gdxpds
import pandas as pd
from pathlib import Path
import yaml
from data.constants import get_country_name

# Store only levels (values) > 0.001
# Used in `clean_results` function
THRESHOLD = 1e-3


def load_config():
    config_path = Path("dashboard/dashboard_config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {
        "results_path": "example_scenarios",
        "geojson_path": "dashboard/shapes/europe_onshore.geojson",
        "gams_path": "/Library/Frameworks/GAMS.framework/Versions/53/Resources/",
    }


def load_standard_scenarios(base_path: str | Path) -> dict[str, Path]:
    # Looks for model-generated scenarios: base_path/scenario_name/results.gdx
    base_path = Path(base_path)
    scenarios = {
        gdx.parent.name: gdx for gdx in sorted(base_path.glob("*/results.gdx"))
    }

    if not scenarios:
        raise FileNotFoundError(
            f"No standard scenario files found in '{base_path}'. "
            "Expected subfolder structure like: base_path/<scenario_name>/results.gdx"
        )

    return scenarios


def load_custom_scenarios(folder_path: str | Path) -> dict[str, Path]:
    # Looks for flat GDX files: folder_path/scenario_name.gdx
    folder_path = Path(folder_path)
    scenarios = {gdx.stem: gdx for gdx in sorted(folder_path.glob("*.gdx"))}

    if not scenarios:
        raise FileNotFoundError(
            f"No custom GDX files found directly in '{folder_path}'. "
            "Expected files like: folder_path/<scenario_name>.gdx"
        )

    return scenarios


def load_scenarios(scenarios_path: str | Path) -> dict[str, Path]:
    scenarios = {}

    # Try loading standard structure
    try:
        scenarios.update(load_standard_scenarios(scenarios_path))
    except FileNotFoundError:
        pass

    # Try loading custom structure
    try:
        scenarios.update(load_custom_scenarios(scenarios_path))
    except FileNotFoundError:
        pass

    if not scenarios:
        raise FileNotFoundError(
            f"No valid GDX scenarios found in '{scenarios_path}' using either standard or custom layouts."
        )

    return scenarios


def load_results(
    gdx_path: str | Path, gams_path: str | Path, variables: list[str]
) -> dict:
    gdx_path = Path(gdx_path)

    results = {}
    with gdxpds.gdx.GdxFile(lazy_load=True, gams_dir=str(gams_path)) as gdx:
        gdx.read(str(gdx_path))
        for var in variables:
            if var in gdx:
                gdx[var].load()
                results[var] = gdx[var].dataframe.copy()
    return results


def load_sets(gdx_path: str | Path, gams_path: str | Path, sets: list[str]) -> dict:
    gdx_path = Path(gdx_path)
    results = {}

    with gdxpds.gdx.GdxFile(lazy_load=True, gams_dir=str(gams_path)) as gdx:
        gdx.read(str(gdx_path))

        for s in sets:
            if s not in gdx:
                continue

            gdx[s].load()
            df = gdx[s].dataframe.copy().reset_index(drop=True)

            # need to seperate different types of sets
            if df.shape[0] == 1 and len(df.columns) >= 1:
                results[s] = {"type": "scalar", "value": df.iloc[0, 0]}
            else:
                results[s] = {"type": "table", "data": df}

    return results


def clean_results(results: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    cleaned = {}
    for name, df in results.items():
        df = df.rename(columns={"vre": "g"})
        dims = [
            c
            for c in df.columns
            if c in ("g", "s", "r", "z", "z_alias", "trans", "vre")
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


def scalar(sets, key):
    return sets[key]["value"]


def table(sets, key):
    return sets[key]["data"]


def check_user_config(config):
    errors = []

    # 1. Check results path
    results_path = config.get("results_path")
    if results_path and not Path(results_path).is_dir():
        errors.append(f"Results folder does not exist: `{results_path}`")

    # 2. Check GeoJSON file path
    geojson_path = config.get("geojson_path")
    if not geojson_path or not Path(geojson_path).is_file():
        errors.append(f"GeoJSON file does not exist: `{geojson_path}`")

    # 3. Check GAMS directory path
    gams_path = config.get("gams_path")
    if not gams_path or not Path(gams_path).is_dir():
        errors.append(
            f"GAMS directory does not exist or GAMS is not installed at: `{gams_path}`"
        )

    return len(errors) == 0, errors
