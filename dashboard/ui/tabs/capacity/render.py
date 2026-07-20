import streamlit as st
from ..figures import render_capacity_pies, render_tot_bar_chart
from ui.components import filter_countries
from data.constants import TECH_ICONS
from ..shared.key_data import render_key_data
from data_loader import table


def render_capacity(df, sets):
    st.title("Capacity Data")

    render_key_data(df, sets)

    _render_capacity_overview(df, sets)


def _render_capacity_overview(df, sets):
    vre_table = table(sets, "vre")
    vre_techs = list(vre_table["g"])
    cap_type = st.radio(
        "Capacity type",
        options=["Total", "New"],
        horizontal=True,
    )
    var = "var_tot_pcap_z" if cap_type == "Total" else "var_new_pcap_z"
    all = (
        df[var]
        .groupby("country_name")["value"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    # Top 5 countries by total installed
    top5 = all.head(5)

    col_countries, col_util = st.columns(2, gap="large")

    with col_countries:
        with st.container(border=True):
            st.caption("TOP 5 COUNTRIES BY INSTALLED CAPACITY")
            for i, row in top5.iterrows():
                st.metric(
                    f"{i + 1}.{row['country_name']}",
                    f"{row['value']:.0f} GW",
                )
            with st.expander(":material/public: &nbsp; See all"):
                st.dataframe(all)

    with col_util:
        with st.container(border=False):
            st.caption(f"{cap_type.upper()} INSTALLED CAPACITY BY TECHNOLOGY")
            var = "var_tot_pcap" if cap_type == "Total" else "var_new_pcap"
            tech_totals = (
                df[var]
                .groupby("g")["value"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            vre = tech_totals[tech_totals["g"].isin(vre_techs)]
            non_vre = tech_totals[~tech_totals["g"].isin(vre_techs)]

            sub1, sub2 = st.columns(2, border=True, gap="large")
            with sub1:
                st.caption("Renewable Technologies")
                for _, row in vre.iterrows():
                    icon = TECH_ICONS.get(row["g"], ":material/category:")
                    st.metric(f"{icon} {row['g']}", f"{row['value']:.1f} GW")
            with sub2:
                st.caption("Other Technologies")
                for _, row in non_vre.iterrows():
                    icon = TECH_ICONS.get(row["g"], ":material/category:")
                    st.metric(f"{icon} {row['g']}", f"{row['value']:.1f} GW")

    st.divider()

    # Explore installed pcap
    _render_explore_installed_pcap(df, cap_type, top5, vre_techs)


def _render_explore_installed_pcap(df, cap_type, top5, vre_techs):
    st.subheader("What's been installed by countries?")

    tech_filter = st.radio(
        "Technologies",
        options=["All", "Renewables only"],
        horizontal=True,
    )

    var = "var_tot_pcap_z" if cap_type == "Total" else "var_new_pcap_z"
    focused = df[var]

    all_var_str = var.split("_z")[0]
    all = df[all_var_str]

    show_vre_only = tech_filter == "Renewables only"

    if show_vre_only:
        df_filtered = focused[focused["g"].isin(vre_techs)]
        all_filtered = all[all["g"].isin(vre_techs)]
    else:
        df_filtered = focused
        all_filtered = all

    st.subheader("All Countries")
    render_tot_bar_chart(all_filtered)

    st.subheader("By Countries")

    top5list = top5["country_name"].tolist()

    col1, col2 = st.columns([3, 1])
    with col1:
        filtered = filter_countries(df_filtered, top5list, key="filter_tot_pcap")
    with col2:
        cols = st.slider("Columns", min_value=1, max_value=6, value=5)

    fig = render_capacity_pies(filtered, cols=cols)
    st.plotly_chart(fig)

    with st.expander("See data table"):
        st.dataframe(filtered)
