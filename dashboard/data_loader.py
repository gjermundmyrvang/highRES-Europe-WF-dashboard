import gdxpds
import pandas as pd
from pathlib import Path

# TODO: Fetch available datasets and let users select with maybe some defaults
VARIABLES = [
    "var_new_pcap",
    "var_new_pcap_z",
    "var_tot_pcap",
    "var_tot_pcap_z",
]

THRESHOLD = 1e-3 # Store only levels (values) > 0.001

def find_result_files(base_path: str | Path = "..") -> dict[str, Path]:
    base_path = Path(base_path)
    gdx_files = sorted(base_path.glob("work*/BASE_*/results.gdx"))
    
    return {p.parent.name: p for p in gdx_files}


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
        dims = [c for c in df.columns if c in ("g", "z")]
        cleaned[name] = (
            df[dims + ["Level"]]
            .rename(columns={"Level": "value"})
            .query("value > @THRESHOLD")
            .reset_index(drop=True)
        )
    return cleaned