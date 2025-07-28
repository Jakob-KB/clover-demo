# /src/utils.py

import os
import random
import requests
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

SUPABASE_FUNCTIONS_URL = f"{os.getenv('SUPABASE_URL')}/functions/v1"
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "https://clover-llm.duckdns.org/api")


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
    """
    Stream assistant response in chunks from FastAPI backend.
    """
    url = f"{FASTAPI_BASE_URL}/conversations/{conversation_id}/turn"
    headers = _auth_headers()

    response = requests.post(
        url,
        headers=headers,
        json={"user_message": user_message},
        stream=True,
        timeout=30,
        verify=False
    )
    response.raise_for_status()

    full_response = ""
    for chunk in response.iter_lines(decode_unicode=True):
        if chunk:
            full_response += chunk
            yield chunk

    return full_response

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


# Generate random conversation name
def get_random_conversation_name() -> str:
    ADJECTIVES = [
        "Crimson", "Emerald", "Sapphire", "Golden", "Silent",
        "Hidden", "Quantum", "Luminous", "Wandering", "Infinite",
        "Velvet", "Mystic", "Solar", "Celestial", "Radiant",
        "Obsidian", "Arcane", "Eternal", "Vivid", "Serene"
    ]
    NOUNS = [
        "Echo", "Odyssey", "Mosaic", "Voyage", "Spectrum",
        "Whisper", "Cipher", "Frontier", "Archive", "Nexus",
        "Horizon", "Pulse", "Vertex", "Enigma", "Mirage",
        "Zenith", "Aurora", "Cascade", "Labyrinth", "Haven"
    ]
    return f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}-{random.randint(0, 99)}"
