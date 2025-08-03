# /src/utils.py

import random
import requests

import streamlit as st
from supabase import create_client
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_ANON_KEY")
SUPABASE_FUNCTIONS_URL = f"{SUPABASE_URL}/functions/v1"

FASTAPI_BASE_URL = st.secrets.get("FASTAPI_BASE_URL")


# Headers
def _auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.jwt}",
        "apikey": SUPABASE_KEY,
    }


# Fetch conversations list
@st.cache_data(ttl=30)
def fetch_conversations():
    response = requests.get(
        f"{SUPABASE_FUNCTIONS_URL}/conversations",
        headers=_auth_headers(),
        timeout=5
    )
    response.raise_for_status()
    return response.json()


# Fetch conversation turns
@st.cache_data(ttl=30)
def fetch_conversation_history(convo_id: str):
    response = requests.get(
        f"{SUPABASE_FUNCTIONS_URL}/turns",
        headers=_auth_headers(),
        params={"conversation_id": convo_id},
        timeout=5
    )
    response.raise_for_status()
    turns = response.json()

    messages = []
    for turn in turns:
        if user_msg := turn.get("user_message"):
            messages.append({"role": "user", "content": user_msg})
        if assistant_msg := turn.get("assistant_response"):
            messages.append({"role": "assistant", "content": assistant_msg})
    return messages


# Create new conversation
def create_conversation(conversation_name: str | None = None, system_prompt: str | None = None) -> dict:
    if conversation_name is None:
        conversation_name = get_random_conversation_name()

    response = requests.post(
        f"{SUPABASE_FUNCTIONS_URL}/conversations",
        headers=_auth_headers(),
        json={
            "name": conversation_name,
            "system_prompt": system_prompt
          },
        timeout=5
    )
    response.raise_for_status()
    return response.json()


def update_conversation_name(convo_id: str, new_name: str):
    """
    Update the name of a conversation using its ID.
    Returns True if successful, False otherwise.
    """
    authed_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    authed_client.postgrest.auth(st.session_state.jwt)

    authed_client.table("conversations") \
        .update({"name": new_name}) \
        .eq("id", convo_id) \
        .execute()


def fetch_system_prompt(convo_id: str) -> str | None:
    """
    Fetch only the system_prompt using an authenticated Supabase client with the user's JWT.
    """
    # Create a new client with a custom auth header
    authed_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    authed_client.postgrest.auth(st.session_state.jwt)

    response = authed_client.table("conversations") \
        .select("system_prompt") \
        .eq("id", convo_id) \
        .single() \
        .execute()

    if response.data and isinstance(response.data, dict):
        return response.data.get("system_prompt")

    return None


# Send a new turn (user message) to the backend
def send_turn(conversation_id: str, user_message: str) -> str:
    """
    Send user message to FastAPI backend and return the assistant's response.
    """
    url = f"{FASTAPI_BASE_URL}/conversations/{conversation_id}/turn"
    headers = _auth_headers()

    response = requests.post(
        url,
        headers=headers,
        json={"user_message": user_message},
        timeout=30,
        verify = False
    )

    response.raise_for_status()
    return response.json().get("assistant_response", "")


# Stream assistant response chunks for a new turn
def stream_chunks(conversation_id: str, user_message: str):
    url  = f"{FASTAPI_BASE_URL}/conversations/{conversation_id}/turn"
    resp = requests.post(url, headers=_auth_headers(),
                         json={"user_message": user_message},
                         stream=True, timeout=30, verify=False)
    resp.raise_for_status()

    for chunk in resp.iter_content(chunk_size=1024, decode_unicode=True):
        if chunk:
            yield chunk               # chunk already contains any "\n"s



def delete_conversation(conversation_id: str):
    """
    Permanently delete a conversation via the Supabase Edge Function.
    """
    response = requests.delete(
        f"{SUPABASE_FUNCTIONS_URL}/conversations/{conversation_id}",
        headers=_auth_headers(),
        timeout=5,
        verify=False
    )
    response.raise_for_status()


def get_random_conversation_name() -> str:
    ADJECTIVES = [
        "Silent", "Golden", "Quantum", "Majestic", "Frosty", "Shy", "Bold",
        "Radiant", "Velvety", "Hidden", "Witty", "Zany", "Lively", "Eager",
        "Rapid", "Swift", "Crimson", "Cosmic", "Bouncy", "Brisk", "Cheery",
        "Gentle", "Mellow", "Chilly", "Curious", "Playful", "Mystic", "Nimble"
    ]

    NOUNS = [
        "Echo", "Pulse", "Labyrinth", "Nexus", "Odyssey", "Signal", "Summit",
        "Vertex", "Mirage", "Beacon", "Galaxy", "Whisper", "Harbor", "Fragment",
        "Crystal", "Voyager", "Orbit", "Flame", "Nova", "Dust", "Cloud", "Meadow",
        "Horizon", "Circuit", "Pattern", "Memory", "Sparkle"
    ]

    number = f"{random.randint(0, 99):02d}"
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)

    while len(adjective) + len(noun) > 16:
        adjective = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)

    return f"{adjective}-{noun}-{number}"


from datetime import datetime, timezone

def time_ago(dt_str=None):
    now = datetime.now(timezone.utc)

    if not dt_str:
        return "???"  # no value

    if isinstance(dt_str, str):
        try:
            dt_str = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            return "???"  # invalid string format

    if not isinstance(dt_str, datetime):
        return "???"

    then = dt_str
    delta = now - then

    seconds = int(delta.total_seconds())
    if seconds <= 30:
        return "0s"
    if seconds <= 60:
        # return f"{seconds}s"
        return "1m"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h"
    days = hours // 24
    return f"{min(days, 99)}d"
