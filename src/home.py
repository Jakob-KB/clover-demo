# /src/home.py

import streamlit as st

def render_home_ui() -> bool:
    st.title("🛠️ Conversation Settings")
    st.info("Changes will only apply to **new** conversations. Note currently **only** system prompt has effect.")

    if deleted_convo_name := st.session_state.get("deleted_convo"):
        st.toast(f"Conversation '{deleted_convo_name}' has been deleted.", icon="🗑️")
        st.session_state.deleted_convo = None

    with st.form("new_convo_form"):
        st.markdown("**Parameters**")
        model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"])
        temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
        rag_chunks = st.number_input("RAG Retrieval Chunks", 1, 10, 5)
        chunk_size = st.number_input("Chunk Size (tokens)", 100, 2000, 500)

        st.markdown("**System Prompt**")
        system_prompt = st.text_area(
            label="System Prompt",
            value=st.session_state.agent_settings["system_prompt"],
            height=200,
            label_visibility="collapsed"
        )

        cols = st.columns(3)
        with cols[0]:
            if st.form_submit_button("✅ Save Settings", use_container_width=True):
                st.session_state.agent_settings["system_prompt"] = system_prompt
                st.rerun()

    return True
