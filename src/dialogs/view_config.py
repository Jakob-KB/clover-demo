# /src/dialogs/view_config.py

import streamlit as st

from src.utils.backend import delete_conversation, update_conversation_name, log_conversation
from src.utils.misc import iso_to_readable


@st.dialog(":material/manufacturing: Conversation Settings", width="large")
def render_view_config_dialog_ui(convo):
    try:
        cols = st.columns([0.2,0.26,0.53])
        with cols[1]:
            st.download_button(
                label="Download Log",
                key="download_convo_log",
                icon=":material/download:",
                data=log_conversation(convo_id=convo["id"]),
                file_name=f"{convo['name']}.txt",
                mime="text/plain"
            )
        with cols[2]:
            text = "Delete" if not st.session_state.get("deletion_confirmation", False) else "Confirm Delete"
            if st.button(label=text, icon=":material/delete:"):
                if st.session_state["deletion_confirmation"]:
                    st.session_state.deleted_convo_name = convo["name"]
                    delete_conversation(convo["id"])

                    if st.session_state.selected_convo == convo:
                        st.session_state.messages = []
                        st.session_state.page = "home"

                    st.cache_data.clear()
                    st.session_state.convos = None
                    st.rerun()
                else:
                    st.session_state["deletion_confirmation"] = True
                    st.rerun(scope="fragment")
        with cols[0]:
            if st.button("Favorite", icon=":material/star:"):
                # Send supabase req to toggle favourite flag for convo id
                pass

        st.write("**Conversation Name**")

        convo_name = st.text_input(
            label="Conversation Name",
            value=convo.get("name", "PLACEHOLDER_NAME"),
            key="convo_name_input",
            label_visibility="collapsed",
            max_chars=20,
            width=420
        )

        # Update convo name here
        if convo_name != convo["name"]:
            update_conversation_name(convo["id"], convo_name)
            convo["name"] = convo_name
            st.session_state.convos = None
            st.cache_data.clear()
            st.rerun()

        agent_config = convo.get("agent_config", {})


        st.markdown(f"""
                **Metadata**
                - **Created At**: `{iso_to_readable(convo.get("created_at", "1970-01-01T00:00:00.000000+00:00"))}`
                - **Updated At**: `{iso_to_readable(convo.get("updated_at", "1970-01-01T00:00:00.000000+00:00"))}`
                - **Turns**: `99`
    
                **Parameters**
                - **Model**: `o9-mini`
                - **Temperature**: `{agent_config.get("temperature", "NA")}`
                - **RAG Retrieval Chunks**: `{agent_config.get("retrieval_documents", "NA")}`
                - **Max Previous Turns**: `{agent_config.get("max_previous_turns", "NA")}`
                - **Max Tokens**: `{agent_config.get("max_tokens", "NA")}`
                - **Max Completion Tokens**: `{agent_config.get("max_completion_tokens", "NA")}`
            """)


        with st.container():
            system_prompt = agent_config.get("system_prompt", "NA")
            st.markdown(
                f"**System Prompt**<div class='scrolling-code-block'>{system_prompt}</div>",
                unsafe_allow_html=True
            )
        st.markdown("")
    except Exception as e:
        st.write(f"something happened: {e}")
