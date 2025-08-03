# /src/sidebar.py

from datetime import datetime

import streamlit as st

from src.utils import fetch_conversations, fetch_conversation_history, create_conversation
from src.components import multi_function_sidebar_button
from src.auth import supabase


@st.cache_data(ttl=30)
def fetch_data(convos):
    def parse_datetime(val):
        if isinstance(val, datetime):
            return val
        elif isinstance(val, str):
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except ValueError:
                return datetime.min
        return datetime.min

    return sorted(convos, key=lambda c: parse_datetime(c["updated_at"]), reverse=True)

def render_sidebar_ui():
    st.sidebar.title("Clover Demo")

    st.session_state.get("clicked_convo_id", None)

    cols = st.sidebar.columns([0.1, 0.475])
    with cols[0]:
        if st.button("", icon=":material/home:"):
            st.session_state.page = "home"
            st.session_state.selected_convo = None
            st.rerun()
    with cols[1]:
        if st.button("New Conversation", key="new_convo", use_container_width=True, icon=":material/add:"):
            try:
                convo = create_conversation(
                    system_prompt=st.session_state.agent_settings["system_prompt"]
                )
                st.cache_data.clear()
                st.session_state.convos = None
                st.session_state.selected_convo = convo
                st.session_state.new_convo_name = convo["name"]
                st.session_state.messages = []
                st.session_state.page = "convo"
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to create conversation: {e}")

    with st.sidebar.expander("Agent Settings", icon=":material/auto_transmission:"):
        st.file_uploader(
            label="**NDIS Plan**",
            type="pdf",
            accept_multiple_files=False,
            disabled=True
        )

        current_value = st.text_area(
            label="**System Prompt**",
            value=st.session_state.agent_settings.get("system_prompt"),
            key="prompt_text_area"
        )

        if current_value != st.session_state.agent_settings.get("system_prompt"):
            st.session_state.agent_settings["system_prompt"] = current_value
            st.toast("System prompt updated.", icon=":material/edit:")

    st.sidebar.markdown("### Chats")

    try:
        if not st.session_state.convos:
            st.session_state.convos = fetch_conversations()

        sorted_convos = fetch_data(st.session_state.convos)

        with st.sidebar.container(height=420, border=False):
            for convo in sorted_convos:
                multi_function_sidebar_button(convo)

    except Exception as e:
        st.sidebar.error(f"Error fetching conversations: {e}")
        st.session_state.convos = []

    st.sidebar.markdown("---")

    if st.sidebar.button("Log Out", icon=":material/logout:"):
        try:
            supabase.auth.sign_out()
        except Exception as e:
            st.warning(f"Logout error: {e}")
        st.session_state.clear()
        st.cache_data.clear()
        st.session_state["initial_login"] = False
        st.rerun()

    clicked_convo_id = st.session_state.get("clicked_convo_id")
    if st.session_state.clicked_convo_id:
        try:
            convo = next(c for c in st.session_state.convos if c["id"] == clicked_convo_id)
            st.session_state.selected_convo = convo
            st.session_state.page = "convo"
            st.session_state.messages = fetch_conversation_history(convo["id"])
        except Exception as e:
            st.sidebar.error(f"Failed to load conversation history: {e}")
            st.session_state.messages = [{"role": "assistant", "content": "SAMPLE MESSAGE"}]
        st.session_state.clicked_convo_id = None
        st.rerun()
