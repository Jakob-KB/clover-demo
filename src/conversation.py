from datetime import datetime, timezone
import re

import streamlit as st

from src.utils import stream_chunks


import re
def format_message(text: str) -> str:
    """
    General-purpose formatter for LLM output.
    Handles code blocks, lists, and poetry formatting while preserving full message content.
    """
    if not text:
        return ""

    # Convert literal \n into real line breaks
    text = text.replace("\\n", "\n")

    # Optional: unwrap code blocks for better line control (not recommended if you want true markdown rendering)
    def unwrap_code_block(match):
        return "\n" + match.group(1).strip() + "\n"

    text = re.sub(r"```(?:[a-z]*\n)?(.*?)```", unwrap_code_block, text, flags=re.DOTALL)

    # Smart sentence-breaking for poems (if not already line-broken)
    if "\n" not in text and text.count(",") >= 3:
        text = re.sub(r"([.,;!?])([A-Z])", r"\1\n\2", text)

    return text.strip()

def render_conversation_ui():
    convo = st.session_state.get("selected_convo")

    if not convo:
        st.title("Clover Demo")
        st.info(":material/info: No conversation selected. Select or create a conversation.")
        return

    st.title(f":material/chat: {convo['name']}")

    # Show past messages
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(format_message(msg["content"]))
            print(f"PAST MESSAGES RAW: \n {msg["content"]}")
            print(f"PAST MESSAGES FORMATTED: \n {format_message(msg["content"])}")

    if not st.session_state.get("messages"):
        st.info(":material/info: Send a message or ask a question to get started.")

    # Prompt handler
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.selected_convo["updated_at"] = datetime.now(timezone.utc)

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            convo_id = convo["id"]
            full_response = ""

            with st.chat_message("assistant"):
                response_box = st.empty()
                for chunk in stream_chunks(convo_id, prompt):
                    full_response += chunk
                    response_box.markdown(full_response + "▌")

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()

        except Exception as e:
            st.error(f"Error while fetching response: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**Error:** {e}"
            })
