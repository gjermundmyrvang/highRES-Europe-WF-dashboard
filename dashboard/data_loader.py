import gdxpds
import pandas as pd
from pathlib import Path

VARIABLES = [
    "var_new_pcap",
    "var_new_pcap_z",
    "var_tot_pcap",
    "var_tot_pcap_z",
    "var_tot_trans_pcap",
    "costs",
    "area"
]

SETS = ["hfirst", "hlast", "day", "month", "year"]

THRESHOLD = 1e-3 # Store only levels (values) > 0.001

def find_work_folders(base_path: str | Path = "..") -> dict[str, dict[str, Path]]:
    base_path = Path(base_path)
    result = {}
    for gdx in sorted(base_path.glob("work*/*/results.gdx")): # Work derived from config file (paths: results)
        work_folder = gdx.parent.parent.name
        scenario    = gdx.parent.name
        result.setdefault(work_folder, {})[scenario] = gdx.parent
    return result

def load_results(gdx_path: str | Path) -> dict[str, pd.DataFrame]:
    gdx_path = Path(gdx_path)
    if not gdx_path.exists():
        raise FileNotFoundError(f"No GDX file found at {gdx_path}")

    results = {}
    with gdxpds.gdx.GdxFile(lazy_load=False) as gdx:
        gdx.read(str(gdx_path))
        for var in VARIABLES:
            if var in gdx:
                results[var] = gdx[var].dataframe.copy()
            else:
                print(f"Warning: {var} not found in {gdx_path.name}")

    return results


def clean_results(results: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    cleaned = {}
    for name, df in results.items():
        df = df.rename(columns={"vre": "g"})
        dims = [c for c in df.columns if c in ("g", "r", "z", "z_alias", "trans", "vre")]
        value_col = next(c for c in df.columns if c.lower() in ("level", "value"))
        cleaned[name] = (
            df[dims + [value_col]]
            .rename(columns={value_col: "value"})
            .query("value > @THRESHOLD")
            .reset_index(drop=True)
        )
    return cleaned

def load_sets(gdx_path: str | Path) -> dict:
    gdx_path = Path(gdx_path)
    sets = {}
    with gdxpds.gdx.GdxFile(lazy_load=False) as gdx:
        gdx.read(str(gdx_path))
        for s in SETS:
            if s in gdx:
                sets[s] = int(gdx[s].dataframe.iloc[0, 0])
    return sets