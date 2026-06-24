import requests
import streamlit as st

@st.cache_data
def get_currencies():
    response = requests.get("https://api.frankfurter.dev/v2/currencies")
    return response.json()

@st.cache_data
def get_exchange_rate(target_currency):
    response = requests.get(
        "https://api.frankfurter.dev/v2/rates",
        params={"base": "GBP", "quotes": target_currency}
    )
    return response.json()[0]["rate"]

def adjust_inflation(gbp_value, factor):
    return gbp_value * factor

def adjust_currency(gbp_value, rate):
    adjusted = gbp_value * rate
    return adjusted