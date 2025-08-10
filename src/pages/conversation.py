from datetime import datetime, timezone
import streamlit as st

from src.utils import query_llm_dev, stream_to_ui


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
            st.markdown(msg["content"])

    if not st.session_state.get("messages"):
        st.info(":material/info: Send a message or ask a question to get started.")

    # Prompt handler
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.selected_convo["updated_at"] = str(datetime.now(timezone.utc))

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            convo_id = convo["id"]
            full_response = ""

            with st.chat_message("assistant"):
                response_box = st.empty()

                with st.spinner("Thinking..."):
                    response_text = query_llm_dev(convo_id, prompt, convo.get("agent_config"))

                for chunk in stream_to_ui(response_text):
                    full_response += chunk
                    response_box.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()

        except Exception as e:
            st.error(f"Error while fetching response: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**Error:** {e}"
            })


