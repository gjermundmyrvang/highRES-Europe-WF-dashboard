TECH_ICONS = {
    "Solar": ":material/sunny:",
    "Windoffshore": ":material/air:",
    "Windonshore": ":material/air:",
    "HydroRoR": ":material/water:",
    "HydroRes": ":material/water:",
    "NaturalgasCCGTwithCCSnewOT": ":material/local_fire_department:",
    "NaturalgasOCGTnew": ":material/local_fire_department:",
    "Biomass": ":material/grass:",
    "BiomassCCS": ":material/grass:",
    "NuclearEPR": ":material/radio_button_checked:",
    "SynCon": ":material/settings_input_component:",
    "WindoffshoreFloat": ":material/air:",
    "Windonshore_OF": ":material/air:",
    "Windonshore_F": ":material/air:",
    "Import": ":material/download:",
    "Windoffshorefloating": ":material/air:",
    "Export": ":material/upload:",
}

TECH_COLORS = {
    "Solar": "#f9d002",
    "Windonshore": "#235ebc",
    "Windoffshore": "#6895dd",
    "WindoffshoreFloat": "#0D3B6E",
    "HydroRoR": "#4adbc8",
    "HydroRes": "#08ad97",
    "NuclearEPR": "#ff8c00",
    "NaturalgasCCGTwithCCSnewOT": "#b20101",
    "NaturalgasOCGTnew": "#d35050",
    "Biomass": "#8E6E53",
    "BiomassCCS": "#6B4F3A",
    "SynCon": "#9B59B6",
    "Windonshore_OF": "#a9cf22",
    "Windonshore_F": "#68800e",
    "Import": "#8a1caf",
    "Windoffshorefloating": "#74c6f2",
    "Export": "#c13a00",
}

VRE_TECHS = {
    "Solar",
    "Windonshore",
    "Windoffshore",
    "WindoffshoreFloat",
    "HydroRoR",
    "Windonshore_OF",
    "Windonshore_F",
    "Windoffshorefloating",
}

# TODO: Find better references?
REFERENCE_AREAS = {
    "Luxembourg": 2586,
    "Greater London": 1572,
    "Berlin": 892,
    "New York City": 783,
    "Oslo": 454,
    "Paris": 105,
    "Monaco": 2,
}


def area_reference(km2: float) -> str:
    if km2 <= 0:
        return ""
    closest = min(REFERENCE_AREAS, key=lambda x: abs(REFERENCE_AREAS[x] - km2))
    ratio = km2 / REFERENCE_AREAS[closest]
    if ratio >= 1.5:
        return f"≈ {round(ratio)}× the size of {closest}"
    elif ratio <= 0.5:
        return f"≈ {round(1/ratio)}× smaller than {closest}"
    else:
        return f"≈ the size of {closest}"


CAPACITY_TO_AREA = {
    "Solar": 0.04,
    "Windoffshore": 0.005,
    "Windonshore": 0.0024,
    "HydroRoR": 0.001,
    "Windonshore_OF": 0.0024,
    "Windonshore_F": 0.0024,
    "Windoffshorefloating": 0.005,
}


def get_capacity_to_area(data: dict) -> dict:
    if "gen_cap2area" in data and not data["gen_cap2area"].empty:
        cap2area = data["gen_cap2area"].set_index("g").to_dict()["value"]
        return cap2area
    return CAPACITY_TO_AREA  # fallback


# TODO: Provide correct key value labels
COST_COMPONENTS = {
    "Generation": {
        "costs_gen_capex": "costs_gen_capex",
        "costs_gen_fom": "costs_gen_fom",
        "costs_gen_varom": "costs_gen_varom",
        "costs_gen_start": "costs_gen_start",
        "costs_gen_vreconnection": "costs_gen_vreconnection",
    },
    "Storage": {
        "costs_store_capex": "costs_store_capex",
        "costs_store_fom": "costs_store_fom",
        "costs_store_varom": "costs_store_varom",
        "costs_store_start": "costs_store_start",
    },
    "Transmission": {
        "costs_trans_capex": "costs_trans_capex",
        "costs_trans_fom": "costs_trans_fom",
    },
}

COUNTRY_NAMES = {
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CH": "Switzerland",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "UK": "United Kingdom",
    "GR": "Greece",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IT": "Italy",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "NL": "Netherlands",
    "NO": "Norway",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SE": "Sweden",
    "SI": "Slovenia",
    "SK": "Slovakia",
}


def get_country_name(code: str, fallback: bool = True) -> str:
    result = COUNTRY_NAMES.get(code.upper())
    if result is None:
        if fallback:
            return code
        raise KeyError(f"Unknown country code: '{code}'")
    return result
