# /src/auth.py

import streamlit as st
from supabase import create_client, Client


SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_ANON_KEY")

DEFAULT_EMAIL = st.secrets.get("DEFAULT_EMAIL")
DEFAULT_PASSWORD = st.secrets.get("DEFAULT_PASSWORD")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def render_login_ui() -> None | bool:
    if st.session_state.user is not None:
        return True

    if st.secrets.get("AUTO_LOGIN") and st.session_state.initial_login:
        try:
            st.spinner("Logging in...")
            result = supabase.auth.sign_in_with_password({
                "email": DEFAULT_EMAIL,
                "password": DEFAULT_PASSWORD,
            })
            st.session_state.user = result.user
            st.session_state.jwt = result.session.access_token
            st.session_state.page = "home"
            st.rerun()
        except Exception as e:
            st.error("Login failed. Please check your credentials.")
            st.exception(e)
        return False

    st.title(":material/account_circle: Login")

    email = st.text_input("Email", value=DEFAULT_EMAIL)
    password = st.text_input("Password", value=DEFAULT_PASSWORD, type="password")

    st.markdown("")

    if st.button("Log In", icon=":material/login:"):
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
