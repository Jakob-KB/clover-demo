import streamlit as st

from src.utils import stream_chunks, delete_conversation, fetch_system_prompt
from src.components import multi_function_button
from streamlit_extras.floating_button import floating_button


def render_conversation_ui():
    if st.session_state.get("selected_convo"):
        st.title(st.session_state.selected_convo['name'])

        multi_function_button("chat_1", convo_name="Daily Standup")

    else:
        st.title("Clover Demo 💭")
        st.info("No conversation selected. Select or create a conversation.")
        return


    # ─── Handle Input and Append Messages ─────────────────────────────
    if prompt := st.chat_input("Type your message..."):
        # Add user message first
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            convo_id = st.session_state.selected_convo["id"]
            full_response = ""

            # Accumulate streamed chunks into final message
            for chunk in stream_chunks(convo_id, prompt):
                full_response += chunk

            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**Error:** {e}"
            })

    # ─── Display Chat Messages ────────────────────────────────────────
    for msg in st.session_state.get("messages", []):
        st.chat_message(msg["role"]).write(msg["content"])

    # Handle FAB button click to open the dialog
    if floating_button(":material/chat: Chat"):
        pass
