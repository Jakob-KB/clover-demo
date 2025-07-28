import os
import streamlit as st
import requests
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

# ─── Load Environment ───────────────────────────────────────────────────────
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_FUNCTIONS_URL = f"{SUPABASE_URL}/functions/v1"

# ─── Constants ──────────────────────────────────────────────────────────────
DEFAULT_EMAIL = "test.user@example.com"
DEFAULT_PASSWORD = "6aI5v8dQ5RNHks0iO3i1fxZ7"

# ─── Supabase Client ────────────────────────────────────────────────────────
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── Style Overrides ────────────────────────────────────────────────────────
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            width: 290px !important;
            min-width: 290px !important;
            max-width: 290px !important;
            flex: 0 0 290px !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        
        .stButton > button {
            text-align: left !important;
            justify-content: flex-start !important;
        }
    </style>
""", unsafe_allow_html=True)

# ─── Session State Init ─────────────────────────────────────────────────────
default_state = {
    "user": None,
    "jwt": None,
    "selected_convo": None,
    "messages": [{"role": "assistant", "content": "How can I help you?"}],
    "new_convo_config_mode": False,
}
for key, val in default_state.items():
    st.session_state.setdefault(key, val)

# ─── Login Page ─────────────────────────────────────────────────────────────
if st.session_state.user is None:
    st.set_page_config(page_title="Clover Demo - Login", layout="centered")
    st.title("🔐 Clover Demo Login")
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

# ─── Helper Functions ───────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_conversations():
    headers = {
        "Authorization": f"Bearer {st.session_state.jwt}",
        "apikey": SUPABASE_KEY,
    }
    r = requests.get(f"{SUPABASE_FUNCTIONS_URL}/conversations", headers=headers)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=30)
def fetch_conversation_history(convo_id: str):
    headers = {
        "Authorization": f"Bearer {st.session_state.jwt}",
        "apikey": SUPABASE_KEY,
    }
    r = requests.get(
        f"{SUPABASE_FUNCTIONS_URL}/turns",
        headers=headers,
        params={"conversation_id": convo_id},
        timeout=5
    )
    r.raise_for_status()
    turns = r.json()

    messages = []
    for turn in turns:
        if turn.get("user_message"):
            messages.append({"role": "user", "content": turn["user_message"]})
        if turn.get("assistant_response"):
            messages.append({"role": "assistant", "content": turn["assistant_response"]})
    return messages

def create_conversation():
    st.session_state.new_convo_config_mode = True

# ─── Sidebar ───────────────────────────────────────
with st.sidebar:
    st.title("Clover Demo")
    st.success(f"Logged in as: {st.session_state.user.email}")

    cols_ = st.columns([0.85, 0.25])
    with cols_[0]:
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.selected_convo = None
            pass
    with cols_[1]:
        if st.button("⚙️"):
            create_conversation()

    st.markdown("")
    st.write("**Chats**")

    try:
        conversations = fetch_conversations()

        with st.container(height=300):
            for convo in sorted(conversations, key=lambda c: c["updated_at"], reverse=True):
                if st.button("➤ " + convo["name"], key=f"select_{convo['id']}", use_container_width=True):
                    st.session_state.selected_convo = convo
                    try:
                        history = fetch_conversation_history(convo["id"])
                        st.session_state.messages = [msg for msg in history if msg is not None]
                    except Exception as e:
                        st.error(f"Failed to load conversation history: {e}")
                        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
                    # st.rerun()
                    pass
    except Exception as e:
        st.error(f"Failed to fetch conversations: {e}")

    st.markdown("")

    if st.button("🚪 Logout"):
        try:
            supabase.auth.sign_out()
        except Exception as e:
            st.warning(f"Logout failed: {e}")
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

# ─── New Conversation Config ────────────────────────────────────────────────
if st.session_state.new_convo_config_mode:
    st.set_page_config(page_title="New Conversation Settings")
    st.title("🛠️ New Conversation Settings")
    st.info("Changes to conversation settings will only apply to **new** conversations.")

    with st.form("new_convo_form"):
        st.markdown("**Parameters**")
        model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"])
        temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
        rag_chunks = st.number_input("RAG Retrieval Chunks", 1, 10, 5)
        chunk_size = st.number_input("Chunk Size (tokens)", 100, 2000, 500)

        st.markdown("")
        st.markdown("**System Prompt**")
        system_prompt = st.text_area(
            label="System Prompt",
            value="You are a helpful assistant.",
            height=200,
            label_visibility="collapsed"
        )

        main_col = st.columns(2)
        with main_col[0]:
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Save Settings", use_container_width=True):
                    st.session_state.selected_convo = {
                        "id": "new",
                        "name": "New Chat",
                        "config": {
                            "model": model,
                            "system_prompt": system_prompt,
                            "temperature": temperature,
                            "rag_chunks": rag_chunks,
                            "chunk_size": chunk_size,
                        }
                    }
                    st.session_state.selected_convo = None
                    st.session_state.new_convo_config_mode = False
                    st.cache_data.clear()
                    st.rerun()
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.new_convo_config_mode = False
                    st.rerun()
    st.stop()

# ─── Main Chat Interface ────────────────────────────────────────────────────
st.set_page_config(page_title="Clover Demo")
st.title("Clover Demo 💭")

if st.session_state.selected_convo:
    config = st.session_state.selected_convo.get("config", {})
    st.subheader(f"Conversation: {st.session_state.selected_convo['name']}")

    with st.expander("🔧 LLM Configuration", expanded=False):
        st.markdown(f"""
        **Parameters**
        - **Model**: `gpt-3.5-turbo`
        - **Temperature**: `0.7`
        - **RAG Retrieval Chunks**: `5`
        - **Chunk Size**: `500`
        - **Past Turns Context**: `6`
        
        **System Prompt**
        """)
        st.code("This is the system Prompt being written out directly.", language=None)

else:
    st.info("No conversation selected. Select or create a conversation.")
    st.stop()

# ─── Chat Display ───────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# ─── Chat Input ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("Type your message..."):
    if not OPENAI_API_KEY:
        st.error("Missing OpenAI API key.")
        st.stop()

    client = OpenAI(api_key=OPENAI_API_KEY)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        response = client.chat.completions.create(
            model=config.get("model", "gpt-3.5-turbo"),
            messages=st.session_state.messages,
            temperature=config.get("temperature", 0.7),
            max_tokens=1024
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)
    except Exception as e:
        st.error(f"OpenAI request failed: {e}")
