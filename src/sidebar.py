# /src/sidebar.py

import streamlit as st
from src.utils import fetch_conversations, fetch_conversation_history, create_conversation
from src.auth import supabase

def render_sidebar_ui():
    st.sidebar.title("Clover Demo")
    st.sidebar.success(f"Logged in as: {st.session_state.user.email}")

    cols = st.sidebar.columns([0.85, 0.25])
    with cols[0]:
        if st.button("➕ New Conversation", key="new_convo", use_container_width=True):
            try:
                convo = create_conversation(
                    system_prompt = st.session_state.agent_settings["system_prompt"]
                )
                st.cache_data.clear()
                st.session_state.selected_convo = convo
                st.session_state.messages = []
                st.session_state.page = "convo"
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to create conversation: {e}")
    with cols[1]:
        if st.button("⚙️", key="open_config"):
            st.session_state.page = "home"
            st.rerun()

    st.sidebar.markdown("### Chats")
    clicked_convo_id = None

    try:
        conversations = fetch_conversations()

        with st.sidebar.container(height=300):
            sorted_convos = sorted(conversations, key=lambda c: c["updated_at"], reverse=True)
            for convo in sorted_convos:
                button_key = f"select_{convo['id']}"

                if st.session_state.selected_convo == convo:
                    button_type = "primary"
                else:
                    button_type = "secondary"

                if st.button(f"⮞   {convo["name"]}", key=button_key, use_container_width=True, type=button_type):
                    clicked_convo_id = convo["id"]
                    break
    except Exception as e:
        st.sidebar.error(f"Error fetching conversations: {e}")
        conversations = []

    st.sidebar.markdown("")

    if st.sidebar.button("🚪 Log Out"):
        try:
            supabase.auth.sign_out()
        except Exception as e:
            st.warning(f"Logout error: {e}")
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

    if clicked_convo_id:
        try:
            convo = next(c for c in conversations if c["id"] == clicked_convo_id)
            st.session_state.selected_convo = convo
            st.session_state.page = "convo"
            st.session_state.messages = fetch_conversation_history(convo["id"])
        except Exception as e:
            st.sidebar.error("Failed to load conversation history.")
            st.session_state.messages = [{"role": "assistant", "content": "SAMPLE MESSAGE"}]
        st.rerun()
