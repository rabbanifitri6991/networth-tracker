"""
supabase_client.py
Initialises and returns an authenticated Supabase client.

Reads credentials from (in order of priority):
  1. .streamlit/secrets.toml  (Streamlit Cloud production)
  2. .env file                 (local development)
  3. Environment variables     (CI / Docker)
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def _get_config() -> tuple[str, str]:
    """Return (SUPABASE_URL, SUPABASE_ANON_KEY) from the best available source."""

    # 1. Streamlit secrets (production on Streamlit Cloud)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        return url, key
    except (KeyError, FileNotFoundError):
        pass

    # 2. Environment variables / .env file
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_ANON_KEY", "")
    return url, key


def get_site_url() -> str:
    """Return the deployed app URL (used for OAuth redirect)."""
    try:
        return st.secrets.get("SITE_URL", "http://localhost:8501")
    except FileNotFoundError:
        return os.getenv("SITE_URL", "http://localhost:8501")


def get_anon_client() -> Client:
    """
    Returns a Supabase client using the anon key.
    Used for auth operations (sign in, sign up).
    """
    url, key = _get_config()
    if not url or not key:
        st.error(
            "⚠️ Supabase credentials not found. "
            "Please set SUPABASE_URL and SUPABASE_ANON_KEY in your secrets."
        )
        st.stop()
    return create_client(url, key)


def get_authed_client() -> Client:
    """
    Returns a Supabase client authenticated with the current user's session.
    Row Level Security (RLS) policies will automatically scope all queries
    to the logged-in user's data.
    """
    url, key = _get_config()
    client = create_client(url, key)

    access_token  = st.session_state.get("access_token", "")
    refresh_token = st.session_state.get("refresh_token", "")

    if access_token and refresh_token:
        try:
            client.auth.set_session(access_token, refresh_token)
        except Exception:
            # Session expired — clear and force re-login
            for k in ("access_token", "refresh_token", "user"):
                st.session_state.pop(k, None)
            st.rerun()

    return client


def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))


def get_current_user() -> dict | None:
    return st.session_state.get("user")


def sign_out() -> None:
    """Clear session state and sign out from Supabase."""
    try:
        client = get_anon_client()
        client.auth.sign_out()
    except Exception:
        pass
    for k in ("access_token", "refresh_token", "user", "page"):
        st.session_state.pop(k, None)
