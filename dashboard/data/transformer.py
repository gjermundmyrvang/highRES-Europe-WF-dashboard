import geopandas as gpd


def load_country_areas(geojson_path: str) -> dict[str, float]:
    gdf = gpd.read_file(geojson_path)
    # EPSG: 3035: The official standard for pan-European statistical analysis, land use (from google search)
    gdf = gdf.to_crs("EPSG:3035")
    gdf["area_km2"] = gdf.geometry.area / 1e6  # 10**6
    return dict(zip(gdf["index"], gdf["area_km2"]))
