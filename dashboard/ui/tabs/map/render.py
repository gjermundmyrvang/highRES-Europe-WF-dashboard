import streamlit as st
from data.clean_transmission import remove_duplicate_pairs
from shapely.geometry import shape

def render_map(df, geo):
    st.title("Map Exploration")

    tot_z = df["var_tot_pcap_z"]
    tot_trans = remove_duplicate_pairs(df["var_tot_trans_pcap"])

    centroids = {}
    for feature in geo["features"]:
        zone = feature["properties"]["index"]
        centroid = shape(feature["geometry"]).centroid
        centroids[zone] = (centroid.y, centroid.x)  # lat, lon

    st.dataframe(tot_z)
    st.dataframe(tot_trans)
    st.dataframe(centroids)


