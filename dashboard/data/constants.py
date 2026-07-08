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
}

TECH_COLORS = {
    "Solar": "#F5C518",
    "Windonshore": "#4A90D9",
    "Windoffshore": "#1B5FA8",
    "WindoffshoreFloat": "#0D3B6E",
    "HydroRoR": "#2ECC71",
    "HydroRes": "#1A8C4E",
    "NuclearEPR": "#E74C3C",
    "NaturalgasCCGTwithCCSnewOT": "#7F8C8D",
    "NaturalgasOCGTnew": "#95A5A6",
    "Biomass": "#8E6E53",
    "BiomassCCS": "#6B4F3A",
    "SynCon": "#9B59B6",
}

VRE_TECHS = {"Solar", "Windonshore", "Windoffshore", "WindoffshoreFloat", "HydroRoR"}

# TODO: Find out where to find this information from the official repo files
COUNTRY_AREA_KM2 = {
    "AT": 83871,
    "BE": 30528,
    "BG": 110879,
    "CH": 41285,
    "CZ": 78866,
    "DE": 357114,
    "DK": 42924,
    "EE": 45228,
    "ES": 505990,
    "FI": 338145,
    "FR": 551695,
    "GR": 131957,
    "HR": 56594,
    "HU": 93028,
    "IE": 70273,
    "IT": 301340,
    "LT": 65300,
    "LU": 2586,
    "LV": 64589,
    "NL": 41543,
    "NO": 385207,
    "PL": 312696,
    "PT": 92212,
    "RO": 238397,
    "SE": 450295,
    "SI": 20273,
    "SK": 49035,
    "UK": 243610,
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
