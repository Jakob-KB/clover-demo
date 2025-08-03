# /src/dialog.py

import streamlit as st

from src.utils import delete_conversation, fetch_system_prompt, update_conversation_name


@st.dialog(":material/manufacturing: Conversation Settings", width="large")
def conversation_settings_dialog(convo):
    settings = st.session_state.agent_settings

    cols = st.columns([0.31,0.9])
    with cols[0]:
        st.download_button(
            label="Download Log",
            key="download_convo_lo3243244g",
            icon=":material/download:",
            data="PLACEHOLDER. LOG EDGE FUNCTION NEEDS IMPLEMENTATION.",
            file_name=f"{convo['name']}.txt",
            mime="text/plain",
            disabled=True
        )
    with cols[1]:
        text = "Delete " if not st.session_state["deletion_confirmation"] else "Confirm Delete"
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

    st.write("**Conversation Name**")

    convo_name = st.text_input(
        label="Conversation Name",
        value=convo["name"],
        key="conversation_name_input",
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

    st.markdown(f"""
            **Metadata**
            - **Created At**: `09/09/2029`
            - **Updated At**: `09/09/2029`
            - **Turns**: `99`

            **Parameters**
            - **Model**: `{settings.get("model", "o9-mini")}`
            - **Temperature**: `{settings.get("temperature", 0.99)}`
            - **RAG Retrieval Chunks**: `{settings.get("rag_chunks", 9)}`
            - **Chunk Size**: `{settings.get("chunk_size", 999)}`
            - **Past Turns Context**: `{settings.get("past_turns_context", 9)}`
        """)
    with st.container():
        system_prompt = fetch_system_prompt(convo["id"])
        st.markdown(
            f"**System Prompt**<div class='scrolling-code-block'>{system_prompt}</div>",
            unsafe_allow_html=True
        )
    st.markdown("")
