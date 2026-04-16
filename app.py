"""
app.py
Net Worth Tracker — Streamlit entry point.

Run locally:
    streamlit run app.py

Deploy: push to GitHub → connect to Streamlit Community Cloud.
"""

import streamlit as st

# ---- Page config (must be first Streamlit call) ----------------------------
st.set_page_config(
    page_title="Net Worth Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Imports after page config ---------------------------------------------
from supabase_client import is_logged_in, sign_out, get_current_user
from i18n import get_text, SUPPORTED_LANGUAGES
from utils.currency import SUPPORTED_CURRENCIES

# ---- Custom CSS ------------------------------------------------------------
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { background-color: #0f172a; }
        [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
        .stApp { background-color: #0d1117; color: #e2e8f0; }
        [data-testid="metric-container"] {
            background: #1e293b;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #334155;
        }
        [data-testid="stExpander"] { border: 1px solid #334155; border-radius: 10px; }
        hr { border-color: #1e293b; }
        footer { visibility: hidden; }
        /* Auth page */
        .stTabs [data-baseweb="tab-list"] { background: #1e293b; border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Session defaults ------------------------------------------------------
if "language" not in st.session_state:
    st.session_state["language"] = "en"
if "currency" not in st.session_state:
    st.session_state["currency"] = "RM"
if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"


# ============================================================================
# 1. Handle OAuth callback (runs before any other render)
# ============================================================================
if not is_logged_in():
    from components.auth import handle_oauth_callback
    if handle_oauth_callback():
        st.rerun()


# ============================================================================
# 2. Auth gate — show login page if not logged in
# ============================================================================
if not is_logged_in():
    from components.auth import render as render_auth
    render_auth()
    st.stop()   # Don't render anything below this line


# ============================================================================
# 3. Main app (only reaches here if logged in)
# ============================================================================

lang     = st.session_state["language"]
currency = st.session_state["currency"]
t        = lambda key: get_text(key, lang)
user     = get_current_user()

# ---- Sidebar ---------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 16px 0 8px 0;">
            <span style="font-size:2.5rem;">💰</span><br>
            <span style="font-size:1.2rem; font-weight:700; color:#00d4aa;">
                Net Worth Tracker
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Logged-in user info
    if user:
        st.caption(f"👤 {user.get('email', '')}")
    st.divider()

    # ---- Navigation ----
    pages = {
        "dashboard":   f"🏠  {t('nav_dashboard')}",
        "assets":      f"📈  {t('nav_assets')}",
        "liabilities": f"📉  {t('nav_liabilities')}",
        "networth":    f"📊  {t('nav_networth')}",
        "goals":       f"🎯  {t('nav_goals')}",
        "how_long":    f"⏳  {t('nav_how_long')}",
    }

    for page_key, label in pages.items():
        is_active = st.session_state["page"] == page_key
        if st.button(
            label,
            key=f"nav_{page_key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state["page"] = page_key
            st.rerun()

    st.divider()

    # ---- Settings ----
    st.markdown("**⚙️ Settings**")

    lang_name = st.selectbox(
        t("language"),
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=list(SUPPORTED_LANGUAGES.values()).index(lang),
        key="lang_selector",
    )
    new_lang = SUPPORTED_LANGUAGES[lang_name]
    if new_lang != st.session_state["language"]:
        st.session_state["language"] = new_lang
        st.rerun()

    currency_sel = st.selectbox(
        t("currency"),
        options=SUPPORTED_CURRENCIES,
        index=SUPPORTED_CURRENCIES.index(currency),
        key="currency_selector",
    )
    if currency_sel != st.session_state["currency"]:
        st.session_state["currency"] = currency_sel
        st.rerun()

    st.caption(t("currency_note"))
    st.divider()

    if st.button("🚪  Sign Out", use_container_width=True):
        sign_out()
        st.rerun()

    st.caption("v2.0.0 · Built with Streamlit + Supabase")


# ---- Page Router -----------------------------------------------------------
page = st.session_state["page"]

if page == "dashboard":
    from components.dashboard import render
    render(lang, currency)

elif page == "assets":
    from components.assets import render
    render(lang, currency)

elif page == "liabilities":
    from components.liabilities import render
    render(lang, currency)

elif page == "networth":
    from components.networth import render
    render(lang, currency)

elif page == "goals":
    from components.goals import render
    render(lang, currency)

elif page == "how_long":
    from components.how_long import render
    render(lang, currency)
