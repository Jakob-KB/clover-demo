# /src/utils.py

import requests
from typing import Dict
import json

import streamlit as st
import urllib.parse
import urllib3

from src.utils.misc import iso_to_readable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SUPABASE_FUNCTIONS_URL = f"{st.secrets.get("SUPABASE_URL")}/functions/v1"

USE_DEDICATED_SERVER: bool = True
if USE_DEDICATED_SERVER:
    FASTAPI_BASE_URL = st.secrets.get("FASTAPI_BASE_URL")  # For testing using dedicated server API
else:
    FASTAPI_BASE_URL = "http://127.0.0.1:8000/api"  # For testing using a locally hosted API

# Headers
def _auth_headers():
    auth = {
        "Authorization": f"Bearer {st.session_state.jwt}",
    }
    return auth

# Backend Connections
@st.cache_data(ttl=30)
def fetch_conversations():
    response = requests.get(
        f"{SUPABASE_FUNCTIONS_URL}/conversations",
        headers=_auth_headers(),
        timeout=5
    )
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=30)
def fetch_conversation_turns(convo_id: str):
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

def create_conversation(conversation_name: str, agent_config: dict | None = None) -> dict:
    response = requests.post(
        f"{SUPABASE_FUNCTIONS_URL}/conversations",
        headers=_auth_headers(),
        json={
            "name": conversation_name,
            "agent_config": agent_config
          },
        timeout=5
    )
    response.raise_for_status()
    return response.json()

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

def log_conversation(convo_id: str) -> str:

    resp = requests.get(
        f"{SUPABASE_FUNCTIONS_URL}/log",
        headers=_auth_headers(),
        params={"conversation_id": convo_id},
        timeout=10,
        verify=False,
    )
    resp.raise_for_status()

    text = resp.text

    # First parse attempt
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"Could not decode JSON from log endpoint: {e}")
        return text

    # If what we got is itself a JSON‐string, parse again
    if isinstance(parsed, str):
        try:
            log = json.loads(parsed)
        except json.JSONDecodeError as e:
            st.error(f"Could not decode nested JSON: {e}")
            return parsed
    else:
        log = parsed

    # Now `log` is a dict
    conv = log.get("conversation", {})
    lines: list[str] = []

    # --- Header ---
    lines.append(f"Conversation: {conv.get('name')}  (ID: {conv.get('id')})")
    lines.append(f"Created:      {iso_to_readable(conv.get('created_at', ''))}")
    lines.append(f"Last updated: {iso_to_readable(conv.get('updated_at', ''))}")
    lines.append("")
    lines.append("Agent configuration:")
    for key, val in conv.get("agent_config", {}).items():
        lines.append(f"  • {key}: {val}")
    lines.append("")

    # --- Transcript ---
    lines.append("Transcript:")
    for idx, turn in enumerate(log.get("turns", []), start=1):
        user_msg = turn.get("user_message", "").strip()
        assistant_msg = turn.get("assistant_response", "").strip()
        lines.append("--- User ---")
        lines.append(user_msg)
        lines.append("")
        lines.append("--- Assistant ---")
        lines.append(assistant_msg)
        lines.append("")
        lines.append("")


    # --- Full raw log for debugging ---
    lines.append("––– Full raw log JSON –––")
    lines.append(json.dumps(log, indent=2))

    return "\n".join(lines)

def update_conversation_name(convo_id: str, new_name: str):
    """
    Update the name of a conversation using its ID.
    """
    st.session_state.supabase_client.postgrest.auth(st.session_state.jwt)
    st.session_state.supabase_client.table("conversations").update({"name": new_name}).eq("id", convo_id).execute()

def query_llm_standard(conversation_id: str, user_message: str) -> str:
    """
    Send user message to FastAPI backend and return the assistant's response.
    """
    url = f"{FASTAPI_BASE_URL}/conversations/{conversation_id}/turn"
    response = requests.post(
        url,
        headers=_auth_headers(),
        json={"user_message": user_message},
        timeout=30,
        verify = False
    )
    response.raise_for_status()
    return response.json()["assistant_response"]

def query_llm_dev(conversation_id: str, user_message: str, agent_config: Dict):
    """
    Send user message to FastAPI backend and return the assistant's response.
    Dev version of this method allows for sending of a custom agent config.
    """
    url = f"{FASTAPI_BASE_URL}/conversations/{conversation_id}/turn_dev"
    resp = requests.post(
        url,
        headers=_auth_headers(),
        json={
            "user_message": user_message,
            "agent_config": agent_config
        },
        timeout=30,
        verify=False
    )
    resp.raise_for_status()
    return resp.json()["assistant_response"]

def fetch_system_prompt(convo_id: str) -> str | None:
    """
    Fetch only the system_prompt using an authenticated Supabase client with the user's JWT.
    """
    st.session_state.supabase_client.postgrest.auth(st.session_state.jwt)

    response = (
        st.session_state.supabase_client
        .table("conversations")
        .select("system_prompt")
        .eq("id", convo_id)
        .single()
        .execute()
    )

    if response.data and isinstance(response.data, dict):
        return response.data.get("system_prompt")
    return None

def upload_plan(pdf_file):
    """
    Do not implement this feature yet into the production app (have not yet finalized security rules)
    """
    base = st.secrets["SUPABASE_URL"].rstrip("/")
    account_id = st.session_state.user.id
    filename   = urllib.parse.quote_plus(pdf_file.name)
    url = f"{base}/storage/v1/object/ndis-plans/{account_id}/{filename}"

    data = pdf_file.read()

    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {st.session_state.jwt}",
            "apikey": st.secrets["SUPABASE_ANON_KEY"],
            "Content-Type": "application/pdf",
        },
        data=data,
        timeout=10,
        verify=False,
    )
    resp.raise_for_status()

    return resp.json() if resp.headers.get("Content-Type","").startswith("application/json") else None
