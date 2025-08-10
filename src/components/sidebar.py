# /src/sidebar.py

import streamlit as st

from src.utils.misc import get_random_conversation_name, sort_recent_conversations
from src.utils.backend import (
        fetch_conversations,
        fetch_conversation_turns,
        create_conversation,
        upload_plan
    )
from .segment_button import segment_button


def render_sidebar():
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

                system_prompt = st.session_state.set_system_prompt

                if system_prompt == "":
                    system_prompt = st.session_state.default_system_prompt

                # Build agent config
                temp_agent_config = {
                    "system_prompt": system_prompt,
                    "document_prompt": "Here are additional documents that may help answer the users question: {context}",
                    "retrieval_documents": 5,
                    "max_previous_turns": 6,
                    "temperature": 0.4,
                    "max_tokens": 400,
                    "max_completion_tokens": 400,
                }


                convo = create_conversation(
                    conversation_name=get_random_conversation_name(),
                    agent_config=temp_agent_config
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
        uploaded_plan = st.file_uploader(
            label="**NDIS Plan**",
            type="pdf",
            accept_multiple_files=False,
            disabled=st.session_state["disable_file_upload"]
        )

        if uploaded_plan and not st.session_state.get("plan_uploaded"):
            try:
                with st.spinner("Uploading…"):
                    upload_plan(uploaded_plan)
                st.success("✅ Uploaded successfully!")
                st.session_state.plan_uploaded = True
            except Exception as e:
                st.error(f"Upload failed: {e}")

        current_value = st.text_area(
            label="**System Prompt**",
            value=st.session_state.set_system_prompt,
            placeholder="Enter system prompt...",
            key="prompt_text_area"
        )

        if current_value != st.session_state.set_system_prompt:
            st.session_state.set_system_prompt = current_value
            st.toast("System prompt updated.", icon=":material/edit:")


    colsB = st.sidebar.columns([1, 0.15])
    with colsB[0]:
        st.markdown("### Chats")
    with colsB[1]:
        if st.button("", icon=":material/refresh:", type="tertiary"):
            st.cache_data.clear()
            st.rerun()

    try:
        if not st.session_state.convos:
            st.session_state.convos = fetch_conversations()

        sorted_convos = sort_recent_conversations(st.session_state.convos)

        with st.sidebar.container(height=420, border=False):
            for convo in sorted_convos:
                segment_button(convo)

    except Exception as e:
        st.sidebar.error(f"Error fetching conversations: {e}")
        st.session_state.convos = []

    st.sidebar.markdown("---")

    if st.sidebar.button("Log Out", icon=":material/logout:"):
        try:
            st.session_state.supabase_client.auth.sign_out()
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
            st.session_state.messages = fetch_conversation_turns(convo["id"])
        except Exception as e:
            st.sidebar.error(f"Failed to load conversation history: {e}")
            st.session_state.messages = [{"role": "assistant", "content": "SAMPLE MESSAGE"}]
        st.session_state.clicked_convo_id = None
        st.rerun()
