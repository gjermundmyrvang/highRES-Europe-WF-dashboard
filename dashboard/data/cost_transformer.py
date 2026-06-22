import requests

def get_eur_gbp_rate():
    url = "https://api.frankfurter.dev/v2/rates"
    headers = {"Accept": "application/json"}
    params = {"base": "GBP", "quotes": "EUR"}

    response = requests.get(url, headers=headers, params=params)
    parsed = response.json()
    return parsed[0]["rate"]

def adjust_inflation(gbp_value, factor):
    return gbp_value * factor

def adjust_currency(gbp_value, rate):
    adjusted = gbp_value * rate
    return adjusted