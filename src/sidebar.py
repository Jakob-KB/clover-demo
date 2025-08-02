import streamlit as st
from streamlit.components.v1 import html
from src.utils import fetch_conversations, fetch_conversation_history, create_conversation
from src.auth import supabase

def render_sidebar_ui():
    st.sidebar.title("Clover Demo")

    cols = st.sidebar.columns([1])
    with cols[0]:
        if st.button("➕ New Conversation", key="new_convo", use_container_width=True):
            try:
                convo = create_conversation(
                    system_prompt=st.session_state.agent_settings["system_prompt"]
                )
                st.cache_data.clear()
                st.session_state.selected_convo = convo
                st.session_state.messages = []
                st.session_state.page = "convo"
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to create conversation: {e}")

        with st.expander("🛠️ Agent Settings"):
            prompt_key = "system_prompt"
            current_value = st.text_area(
                "System Prompt",
                value=st.session_state.agent_settings[prompt_key],
                key="prompt_text_area"
            )

            if current_value != st.session_state.agent_settings[prompt_key]:
                st.session_state.agent_settings[prompt_key] = current_value
                st.toast("✅ System prompt updated.")

    st.sidebar.markdown("### Chats")
    clicked_convo_id = None

    try:
        conversations = fetch_conversations()
        sorted_convos = sorted(conversations, key=lambda c: c["updated_at"], reverse=True)

        with st.sidebar.container(height=420, border=False):
            for convo in sorted_convos:
                button_label = f"⮞   {convo['name']}"
                button_key = f"select_{convo['id']}"
                button_type = "primary" if st.session_state.selected_convo == convo else "tertiary"

                if st.button(button_label, key=button_key, type=button_type):
                    clicked_convo_id = convo["id"]
                    break


    except Exception as e:
        st.sidebar.error(f"Error fetching conversations: {e}")
        conversations = []

    st.sidebar.markdown("---")

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
