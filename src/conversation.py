# /src/chat.py

import streamlit as st

from src.utils import stream_chunks, delete_conversation, fetch_system_prompt

def render_conversation_ui():
    if st.session_state.get("selected_convo"):
        st.title(st.session_state.selected_convo['name'])

        v1 = st.columns([0.1, 0.18])
        with v1[0]:
            st.download_button(
                label="Download Conversation Log",
                key="download_convo_lo32432g",
                icon=":material/download:",
                data="PLACEHOLDER. LOG EDGE FUNCTION NEEDS IMPLEMENTATION.",
                file_name=f"{st.session_state.selected_convo['name']}.txt",
                mime="text/plain"
            )
        with v1[1]:
            if st.button("🗑️"):
                try:
                    delete_conversation(st.session_state.selected_convo["id"])
                    st.session_state.selected_convo = None
                    st.session_state.messages = []
                    st.cache_data.clear()
                    st.session_state.page = "home"
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete conversation: {e}")

    else:
        st.title("Clover Demo 💭")
        st.info("No conversation selected. Select or create a conversation.")
        return

    settings = st.session_state.agent_settings

    with st.expander("🔧 Agent Settings", expanded=False):
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

        **System Prompt**
        """)

        with st.container():
            st.markdown(
                """
                <style>
                .scrolling-code-block {
                    max-height: 300px;
                    overflow-y: auto;
                    white-space: pre-wrap;  /* wraps long lines */
                    word-break: break-word;
                    background-color: #0e1117;
                    border-radius: 0.5rem;
                    padding: 1rem;
                    font-family: monospace;
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

    st.markdown("")


    # Display Chat History
    for msg in st.session_state.get("messages", []):
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        try:
            convo_id = st.session_state.selected_convo["id"]
            assistant_container = st.chat_message("assistant")
            stream_display = assistant_container.empty()

            full_response = ""
            for chunk in stream_chunks(convo_id, prompt):
                full_response += chunk
                stream_display.markdown(full_response + "▍")

            stream_display.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Failed to stream response: {e}")
