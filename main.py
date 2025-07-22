import os
import streamlit as st
import requests
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

# ─── Constants & Config ─────────────────────────────────────────────────────
DEFAULT_EMAIL = "test.user@example.com"
DEFAULT_PASSWORD = "6aI5v8dQ5RNHks0iO3i1fxZ7"

# ─── Load Environment ───────────────────────────────────────────────────────
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_FUNCTIONS_URL = f"{SUPABASE_URL}/functions/v1"

# ─── Supabase Client ────────────────────────────────────────────────────────
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── Style Overrides ────────────────────────────────────────────────────────
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            width: 270px !important;
            min-width: 270px !important;
            max-width: 270px !important;
            flex: 0 0 270px !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# ─── Session State Init ─────────────────────────────────────────────────────
defaults = {
    "user": None,
    "jwt": None,
    "selected_convo": None,
    "messages": [{"role": "assistant", "content": "How can I help you?"}],
    "new_convo_config_mode": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─── Authentication ─────────────────────────────────────────────────────────
if st.session_state.user is None:
    st.set_page_config(page_title="Clover Chat - Login", page_icon="💬", layout="centered")
    st.title("🔐 Clover Chat Login")
    st.caption("This page is restricted. Please log in to continue.")

    email = st.text_input("Email", value=DEFAULT_EMAIL)
    password = st.text_input("Password", type="password", value=DEFAULT_PASSWORD)

    if st.button("Log In"):
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = result.user
            st.session_state.jwt = result.session.access_token
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
    st.stop()

# ─── Data Functions ─────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_conversations():
    headers = {
        "Authorization": f"Bearer {st.session_state.jwt}",
        "apikey": SUPABASE_KEY
    }
    r = requests.get(f"{SUPABASE_FUNCTIONS_URL}/conversations", headers=headers)
    r.raise_for_status()
    return r.json()

def create_conversation():
    st.session_state.new_convo_config_mode = True

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💬 Clover Chat")
    st.success(f"Logged in as {st.session_state.user.email}")

    if st.button("➕  New conversation"):
        create_conversation()

    st.markdown("---")

    try:
        conversations = fetch_conversations()
        sorted_convos = sorted(conversations, key=lambda c: c["updated_at"], reverse=True)

        for convo in sorted_convos:
            with st.container():
                cols = st.columns([0.8, 0.2], gap="small")
                with cols[0]:
                    if st.button(convo["name"], key=f"select_{convo['id']}", use_container_width=True):
                        pass  # Placeholder
                with cols[1]:
                    with st.popover(""):
                        st.markdown("**Options**")
                        st.button("✏️ Rename", key=f"rename_{convo['id']}")
                        st.button("🗑️ Delete", key=f"delete_{convo['id']}")
    except Exception as e:
        st.error(f"Failed to load conversations: {e}")

    st.markdown("---")
    if st.button("Logout"):
        try:
            supabase.auth.sign_out()
        except Exception as e:
            st.warning(f"Supabase logout failed: {e}")
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

# ─── Full-Screen New Chat Form ──────────────────────────────────────────────
if st.session_state.new_convo_config_mode:
    st.set_page_config(page_title="New Chat Settings", page_icon="🛠️")
    st.title("🛠️ New Chat Configuration")

    with st.form("new_convo_fullscreen_form"):
        model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"])
        system_prompt = st.text_area("System Prompt", "You are a helpful assistant.")
        temperature = st.slider("Temperature", 0.0, 1.5, 0.7, step=0.1)
        chunk_count = st.number_input("RAG Retrieval Chunks", min_value=1, max_value=10, value=5)
        chunk_size = st.number_input("Chunk Size (tokens)", min_value=100, max_value=2000, value=500)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ Create Chat"):
                st.session_state.selected_convo = {
                    "id": "new",
                    "name": "New Chat",
                    "config": {
                        "model": model,
                        "system_prompt": system_prompt,
                        "temperature": temperature,
                        "rag_chunks": chunk_count,
                        "chunk_size": chunk_size,
                    }
                }
                st.session_state.new_convo_config_mode = False
                st.cache_data.clear()
                st.rerun()

        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.new_convo_config_mode = False
                st.rerun()

    st.stop()

# ─── Main Chat UI ───────────────────────────────────────────────────────────
st.set_page_config(page_title="Clover", page_icon="💬")
st.title("Clover 💭")

if st.session_state.selected_convo:
    config = st.session_state.selected_convo.get("config", {})
    st.subheader(f"Conversation: {st.session_state.selected_convo['name']}")

    with st.expander("🔧 Agent Details"):
        st.markdown(f"""
        **Model**: `{config.get('model', 'gpt-3.5-turbo')}`  
        **System Prompt**: _{config.get('system_prompt', 'You are a helpful assistant.')}_
        **Temperature**: `{config.get('temperature', 0.7)}`
        **RAG Retrieval Chunks**: `{config.get('rag_chunks', 5)}`
        **Chunk Size**: `{config.get('chunk_size', 500)}`
        """)
else:
    st.caption("No conversation selected.")

# ─── Chat Interaction ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not OPENAI_API_KEY:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=OPENAI_API_KEY)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = client.chat.completions.create(
        model=st.session_state.selected_convo.get("config", {}).get("model", "gpt-3.5-turbo"),
        messages=st.session_state.messages,
        temperature=st.session_state.selected_convo.get("config", {}).get("temperature", 0.7),
        max_tokens=1024
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
