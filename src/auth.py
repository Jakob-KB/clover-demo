# /src/auth.py

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

DEFAULT_EMAIL = os.getenv("DEFAULT_EMAIL")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def render_login_ui() -> None | bool:
    if st.session_state.user is not None:
        return True

    st.title("🔐 Login")

    email = st.text_input("Email", value=DEFAULT_EMAIL)
    password = st.text_input("Password", value=DEFAULT_PASSWORD, type="password")

    st.markdown("")

    if st.button("Log In"):
        try:
            st.spinner("Logging in...")
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            st.session_state.user = result.user
            st.session_state.jwt = result.session.access_token
            st.session_state.page = "home"
            st.rerun()
        except Exception as e:
            st.error("Login failed. Please check your credentials.")
            st.exception(e)

        return False
