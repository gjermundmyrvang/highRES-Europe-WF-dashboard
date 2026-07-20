import streamlit as st


def filter_countries(df, default=None, key="filter_countries"):
    all_countries = sorted(set(df["country_name"]))
    if default is None:
        default = all_countries[:5]
    selected_countries = st.multiselect(
        "Filter countries",
        options=all_countries,
        default=default,
        key=key,
    )

    if not selected_countries:
        return df

    return df[df["country_name"].isin(selected_countries)]
