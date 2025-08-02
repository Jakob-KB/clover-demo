import streamlit as st

from src.utils import delete_conversation, fetch_system_prompt

# ─── Settings Dialog ────────────────────────────────────────────
@st.dialog("🗑️ Delete Conversation")
def deletion_confirmation_dialog():
    st.write("Are you sure you want to delete conversation 'CONVO_NAME'?")
    if st.button("Delete", type="secondary"):
        try:
            st.session_state.deleted_convo = st.session_state.selected_convo["name"]
            delete_conversation(st.session_state.selected_convo["id"])
            st.session_state.selected_convo = None
            st.session_state.messages = []
            st.cache_data.clear()
            st.session_state.page = "home"
            st.rerun()

        except Exception as e:
            st.session_state.deleted_convo = None
            st.error(f"Failed to delete conversation: {e}")

# ─── Settings Dialog ────────────────────────────────────────────
@st.dialog("🔧 Agent Settings", width="large")
def info():
    settings = st.session_state.agent_settings

    st.download_button(
        label="Download Log",
        key="download_convo_lo3243244g",
        icon=":material/download:",
        data="PLACEHOLDER. LOG EDGE FUNCTION NEEDS IMPLEMENTATION.",
        file_name=f"{st.session_state.selected_convo['name']}.txt",
        mime="text/plain"
    )

    st.markdown(
        f"""
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

            **System Prompt**
        """)

    with st.container():
        st.markdown(
            """
            <style>
            .scrolling-code-block {
                max-height: 300px;
                overflow-y: auto;
                white-space: pre-wrap;
                word-break: break-word;
                background-color: #0e1117;
                border-radius: 0.5rem;
                padding: 1rem;
                font-family: monospace;
                font-size: 14px;
                color: white;
                border: 1px solid #333;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        system_prompt = fetch_system_prompt(st.session_state.selected_convo["id"])
        st.markdown(f"<div class='scrolling-code-block'>{system_prompt}</div>", unsafe_allow_html=True)

    st.markdown("")

