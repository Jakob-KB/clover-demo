import streamlit as st
from time import sleep

from src.dialog import deletion_confirmation_dialog, info


@st.fragment
def multi_function_button(key_prefix: str, convo_name: str = "CONVO_NAME"):
    seg_key = f"{key_prefix}_seg"
    trigger_key = f"{key_prefix}_clear_trigger"

    if trigger_key not in st.session_state:
        st.session_state[trigger_key] = False

    if st.session_state[trigger_key]:
        st.session_state[seg_key] = None
        st.session_state[trigger_key] = False

    seg_value = st.segmented_control(
        "Pick an option",
        default=None,
        options=["Settings", "🗑️ "],
        key=seg_key,
        label_visibility="collapsed"
    )

    if seg_value:
        if seg_value == "Settings":
            info()
        elif seg_value == "🗑️ ":
            deletion_confirmation_dialog()

        sleep(0.05)
        st.session_state[trigger_key] = True
        st.rerun(scope="fragment")

multi_function_button("chat_1", convo_name="Daily Standup")