# main.py

import streamlit as st

# Local Modules
from src.auth import render_login_ui
from src.home import render_home_ui
from src.sidebar import render_sidebar_ui
from src.conversation import render_conversation_ui

# Apply Global Styles
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page Setup
st.set_page_config(page_title="Clover Demo", layout="centered")

# Session State Defaults
st.session_state.setdefault("user", None)
st.session_state.setdefault("jwt", None)
st.session_state.setdefault("clicked_convo_id", None)
st.session_state.setdefault("selected_convo", None)
st.session_state.setdefault("deleted_convo_name", None)
st.session_state.setdefault("new_convo_name", None)
st.session_state.setdefault("convos", None)
st.session_state.setdefault("initial_login", True)
st.session_state.setdefault("messages", [{"role": "assistant", "content": "How can I help you?"}])
st.session_state.setdefault("page", "login")
st.session_state.setdefault("agent_settings", {
    "model": "o9-mini",
    "temperature": "0.99",
    "rag_chunks": "9",
    "chunk_size": "999",
    "system_prompt": "You are a helpful assistant."
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
    render_sidebar_ui()
    render_home_ui()

if st.session_state.page == "convo":
    render_sidebar_ui()
    render_conversation_ui()
