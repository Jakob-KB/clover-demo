# /src/components.py

import streamlit as st

from src.utils.misc import time_ago, pad_convo_label
from src.dialogs.view_config import render_view_config_dialog_ui

@st.fragment()
def segment_button(convo):
    seg_key = f"{convo["id"]}_seg"
    trigger_key = f"{convo["id"]}_clear_trigger"

    if trigger_key not in st.session_state:
        st.session_state[trigger_key] = False

    if st.session_state[trigger_key]:
        st.session_state[seg_key] = None
        st.session_state[trigger_key] = False

    last_turn = time_ago(convo["updated_at"])
    text = pad_convo_label(convo["name"], last_turn)
    options = [text, "⋮"]

    seg_value = st.segmented_control(
        "Pick an option",
        default=None,
        options=options,
        key=seg_key,
        label_visibility="collapsed",
        width="stretch"
    )

    if seg_value:
        if seg_value == options[0]:
            st.cache_data.clear()
            st.session_state.clicked_convo_id = convo["id"]
            st.session_state[trigger_key] = True
            st.rerun()


        elif seg_value == options[1]:
            st.session_state["deletion_confirmation"] = False
            render_view_config_dialog_ui(convo)
            st.session_state[trigger_key] = True
            st.rerun(scope="fragment")
