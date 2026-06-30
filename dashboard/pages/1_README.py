import streamlit as st
from pathlib import Path

st.set_page_config(layout="centered")
st.page_link("app.py", label=":material/keyboard_arrow_left: &nbsp; Homepage")


file = Path(__file__).parent.parent / "README.md"
st.markdown(file.read_text(encoding="utf-8"), unsafe_allow_html=True)
