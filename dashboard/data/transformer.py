import random

import geopandas as gpd


def load_country_areas(geojson_path: str) -> dict[str, float]:
    gdf = gpd.read_file(geojson_path)
    # EPSG: 3035: The official standard for pan-European statistical analysis, land use (from google search)
    gdf = gdf.to_crs("EPSG:3035")
    gdf["area_km2"] = gdf.geometry.area / 1e6  # 10**6
    return dict(zip(gdf["index"], gdf["area_km2"]))


def random_hex_color(seed_str):
    """
    TODO:
    -----
    This is used in `render_capacity_mix` so dimensions with other 'techs' thats does not have a color dict also gets a unique color. However random hex can produce colors that are too dark, too light, or low-contrast against the dashboard background. A better solution should be implemented.
    """
    rng = random.Random(seed_str)
    return "#{:06x}".format(rng.randint(0, 0xFFFFFF))
