import streamlit as st

def filter_countries(df, default=["NO", "DK", "SE"], key="filter_countries"):
    all_countries = sorted(set(df["z"]))
    selected_countries = st.multiselect(
        "Filter countries",
        options=all_countries,
        default=default,
        key=key,
    )

    if not selected_countries: 
        return df

    return df[df["z"].isin(selected_countries)]