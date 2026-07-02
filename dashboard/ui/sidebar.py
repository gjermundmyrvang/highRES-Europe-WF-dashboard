import streamlit as st
from pathlib import Path


def render_sidebar(work_folders: dict):
    with st.sidebar:
        st.header(":material/folder_managed: Scenario Settings")

        all_folders = dict(work_folders)
        if st.session_state.added_scenarios:
            all_folders["added"] = st.session_state.added_scenarios

        selected_folder = st.selectbox(
            "Folder",
            options=list(all_folders.keys()),
        )

        scenarios = all_folders[selected_folder]
        selected_scenario = st.selectbox(
            "Scenario",
            options=list(scenarios.keys()),
        )

        st.subheader(":material/create_new_folder: Add other scenarios")
        folder_path = st.text_input("Folder path")
        if st.button("Scan folder"):
            path = Path(folder_path)
            if not path.exists():
                st.error("Folder not found.")
            else:
                found = {p.stem: p for p in path.glob("*.gdx")}
                if not found:
                    st.warning("No GDX files found in that folder.")
                else:
                    st.session_state.added_scenarios.update(found)
                    st.success(f"Added {len(found)} scenario(s).")
                    st.rerun()

        return scenarios[selected_scenario]
