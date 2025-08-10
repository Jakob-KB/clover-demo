# main.py

import streamlit as st
from supabase import create_client, Client

# Local Modules
from src.pages import (
    render_login_ui,
    render_home_ui,
    render_conversation_ui
)
from src.components import render_sidebar

# Set supabase client
SUPABASE_URL: str = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY: str = st.secrets.get("SUPABASE_ANON_KEY")

DEFAULT_EMAIL: str = st.secrets.get("DEFAULT_EMAIL")
DEFAULT_PASSWORD: str = st.secrets.get("DEFAULT_PASSWORD")

_supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.session_state.supabase_client = _supabase_client



# Apply Global Styles
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page Setup
st.set_page_config(page_title="Clover Demo", layout="centered")

# Session State Defaults
st.session_state.setdefault("user", None)
st.session_state.setdefault("jwt", None)
st.session_state.setdefault("disable_file_upload", True)
st.session_state.setdefault("clicked_convo_id", None)
st.session_state.setdefault("selected_convo", None)
st.session_state.setdefault("deleted_convo_name", None)
st.session_state.setdefault("new_convo_name", None)
st.session_state.setdefault("convos", None)
st.session_state.setdefault("initial_login", True)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("page", "login")
st.session_state.setdefault("use_dedicated_server", True)
st.session_state.setdefault("default_system_prompt", "You are a helpful assistant.")
st.session_state.setdefault("set_system_prompt", st.session_state.default_system_prompt)
st.session_state.setdefault("agent_settings", {
    "model": "o9-mini",
    "temperature": "0.99",
    "rag_chunks": "9",
    "chunk_size": "999",
    "system_prompt": "You are a helpful assistant."
})
st.session_state.setdefault("temp_agent_config", {
    "system_prompt": "Talk like a farmer",
    "document_prompt": "Here are additional documents that may help answer the users question: {context}",
    "retrieval_documents": 5,
    "max_previous_turns": 6,
    "temperature": 0.4,
    "max_tokens": 400,
    "max_completion_tokens": 400,
})


if st.session_state.page == "login":
    render_login_ui()

if deleted_convo_name := st.session_state.get("deleted_convo_name"):
    st.toast(f"Conversation '{deleted_convo_name}' has been deleted.", icon=":material/delete:")
    st.session_state.deleted_convo_name = None

if new_convo_name := st.session_state.get("new_convo_name"):
    st.toast(f"Conversation '{new_convo_name}' has been created.", icon=":material/save:")
    st.session_state.new_convo_name = None

if st.session_state.page == "home":
    render_sidebar()
    render_home_ui()

if st.session_state.page == "convo":
    render_sidebar()
    render_conversation_ui()
