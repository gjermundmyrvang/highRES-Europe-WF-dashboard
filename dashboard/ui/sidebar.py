import streamlit as st
from pathlib import Path
from data_loader import load_custom_scenarios


def render_sidebar(all_scenarios: dict):
    with st.sidebar:
        st.header(":material/folder_managed: Scenario Settings")

        selected_scenario = st.selectbox(
            "Scenario",
            options=list(all_scenarios.keys()),
        )

        st.subheader(":material/create_new_folder: Add other scenarios")
        folder_path = st.text_input("Folder path")
        if st.button("Scan folder"):
            path = Path(folder_path)
            if not path.exists():
                st.error("Folder not found.")
            else:
                found = load_custom_scenarios(path)
                if not found:
                    st.warning("No GDX files found in that folder.")
                else:
                    st.session_state.added_scenarios.update(found)
                    st.session_state.scan_success = f"Added {len(found)} scenario(s)."
                    st.rerun()

        # Workaround to display message after `st.rerun()` fires
        if "scan_success" in st.session_state:
            st.success(st.session_state.scan_success)
            del st.session_state.scan_success

        return all_scenarios[selected_scenario]
