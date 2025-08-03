# /src/home.py

import streamlit as st


def render_home_ui():
    st.title("Clover Demo")
    st.success(f":material/account_circle: Logged in as: {st.session_state.user.email}")

    with st.container(border=False):
        st.markdown("""
            Welcome to the Clover Demo, below is are simple instructions as well as an overview of how to use this tool to interact with and improve the Clover LLM Agent.
            
            - On the sidebar under `Agent Settings` copy or type out a system prompt and input Ctrl+Enter to save.
            - Use the `New Conversation` button on the sidebar to create a new conversation baked with your custom system prompt. **Note:** Changed or updated system prompts do **not** apply retroactively and will only apply to **newly** created conversations.
            - It is recommended that prompts be written in external software, such as Google Docs, and then copied in to `Agent Settings` for the sake of convenience and version control.
            - Conversations are created with randomly generated default names but can be edited within `Conversation  Settings`, the menu button on the left of each conversation.
            - Conversations can be deleted by opening its 'Conversation Settings' clicking the `Delete` button, and then clicking it again to confirm the deletion.
            
            The goal of this tool is to tweak and optimize response style, tone and behaviour by continuously evolving the system prompt. It is not designed as a tool for indepth security, both prompt injection and leaking, testing or validating response accuracy or correctness.
        """)

    st.warning(
        f"""
        :material/warning: Several features are either not yet implemented or are not currently functional, these include:
        - Uploading NDIS Plans through Agent Settings.
        - Downloading a Conversation Log through Conversation Settings.
        - Viewing Agent Parameters or Metadata through Conversation Settings.
        """
    )
