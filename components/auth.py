"""
components/auth.py
Login and Sign-up page.

Supports:
  - Email + Password (sign in & sign up)
  - Google OAuth  (sign in via Google — requires Google provider
                   enabled in Supabase Dashboard → Authentication → Providers)
"""

import streamlit as st
from supabase_client import get_anon_client, get_site_url


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _store_session(session) -> None:
    """Persist Supabase session + user into Streamlit session state."""
    st.session_state["access_token"]  = session.access_token
    st.session_state["refresh_token"] = session.refresh_token
    st.session_state["user"] = {
        "id":    session.user.id,
        "email": session.user.email,
    }


def _handle_email_login(email: str, password: str) -> None:
    try:
        client = get_anon_client()
        res = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        _store_session(res.session)
        st.rerun()
    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid_credentials" in msg:
            st.error("❌ Wrong email or password. Please try again.")
        else:
            st.error(f"❌ Login failed: {msg}")


def _handle_email_signup(email: str, password: str, confirm: str) -> None:
    if password != confirm:
        st.error("❌ Passwords do not match.")
        return
    if len(password) < 6:
        st.error("❌ Password must be at least 6 characters.")
        return
    try:
        client = get_anon_client()
        res = client.auth.sign_up({"email": email, "password": password})
        if res.user and res.session:
            _store_session(res.session)
            st.rerun()
        else:
            # Supabase sent a confirmation email
            st.success(
                "✅ Account created! Check your email to confirm, then sign in."
            )
    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower() or "already been registered" in msg.lower():
            st.error("❌ This email is already registered. Try signing in instead.")
        else:
            st.error(f"❌ Sign up failed: {msg}")


def _handle_google_oauth() -> None:
    """
    Starts Google OAuth flow.
    Supabase redirects back to SITE_URL?code=xxx after authentication.
    The callback is handled in app.py via st.query_params.
    """
    try:
        client  = get_anon_client()
        site_url = get_site_url()
        res = client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": site_url,
                "scopes":      "email profile",
            },
        })
        # Open Google OAuth page in the same tab
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={res.url}">',
            unsafe_allow_html=True,
        )
        st.info("Redirecting to Google... If nothing happens, "
                f"[click here]({res.url}).")
    except Exception as e:
        st.error(f"❌ Google sign-in failed: {e}")


# ---------------------------------------------------------------------------
# OAuth callback (called from app.py)
# ---------------------------------------------------------------------------

def handle_oauth_callback() -> bool:
    """
    If the current URL contains ?code=, exchange it for a session.
    Returns True if login was completed.
    """
    params = st.query_params
    code   = params.get("code")
    if not code:
        return False

    try:
        client  = get_anon_client()
        session = client.auth.exchange_code_for_session({"auth_code": code})
        _store_session(session.session)
        st.query_params.clear()
        return True
    except Exception as e:
        st.error(f"❌ OAuth callback failed: {e}")
        st.query_params.clear()
        return False


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render() -> None:
    st.markdown(
        """
        <div style="text-align:center; padding: 32px 0 8px 0;">
            <span style="font-size:3.5rem;">💰</span><br>
            <span style="font-size:2rem; font-weight:700; color:#00d4aa;">
                Net Worth Tracker
            </span><br>
            <span style="color:#888; font-size:1rem;">
                Track your wealth, month by month
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Centre the form
    _, col, _ = st.columns([1, 2, 1])
    with col:
        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

        # ---- Sign In -------------------------------------------------------
        with tab_login:
            st.markdown("##### Welcome back 👋")

            email    = st.text_input("Email",    key="login_email",    placeholder="you@email.com")
            password = st.text_input("Password", key="login_password", type="password", placeholder="••••••••")

            if st.button("Sign In", key="btn_login", use_container_width=True, type="primary"):
                if email and password:
                    _handle_email_login(email, password)
                else:
                    st.warning("Please enter your email and password.")

            st.markdown("---")

            # Google OAuth
            if st.button("🔵  Sign in with Google", key="btn_google_login", use_container_width=True):
                _handle_google_oauth()

            st.caption(
                "Google sign-in requires the Google provider to be enabled in "
                "your Supabase project → Authentication → Providers."
            )

        # ---- Sign Up -------------------------------------------------------
        with tab_signup:
            st.markdown("##### Create your account")

            new_email    = st.text_input("Email",            key="signup_email",    placeholder="you@email.com")
            new_password = st.text_input("Password",         key="signup_password", type="password", placeholder="Min. 6 characters")
            confirm_pw   = st.text_input("Confirm Password", key="signup_confirm",  type="password", placeholder="Repeat password")

            if st.button("Create Account", key="btn_signup", use_container_width=True, type="primary"):
                if new_email and new_password and confirm_pw:
                    _handle_email_signup(new_email, new_password, confirm_pw)
                else:
                    st.warning("Please fill in all fields.")

            st.markdown("---")

            if st.button("🔵  Sign up with Google", key="btn_google_signup", use_container_width=True):
                _handle_google_oauth()
