"""MEDILEAF.AI — Main Streamlit Application Entry Point (Fixed Desktop Sidebar & 8-Page Flow)."""

from __future__ import annotations

import streamlit as st

from auth.authentication import authenticate_user, get_user_preferences, init_db, register_user
from pages import (
    about,
    dashboard,
    dataset_information,
    identify_leaf,
    model_analytics,
    prediction_history,
    settings,
)
from src.config import ASSETS_DIR, SAFETY_DISCLAIMER

st.set_page_config(
    page_title="MEDILEAF.AI — Medicinal-Leaf Identifier",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _load_css(theme: str = "Light") -> None:
    css_path = ASSETS_DIR / "styles" / "botanical.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    if theme == "Dark":
        st.markdown(
            """
            <style>
              .stApp { background-color: #0B1712 !important; color: #ECFDF5 !important; }
              .medileaf-card { background: #11221B !important; border-color: #1E3B2E !important; color: #ECFDF5 !important; }
              .medileaf-metric-val { color: #FFFFFF !important; }
              .medileaf-metric-label { color: #A7F3D0 !important; }
              .medileaf-disclaimer { background: #152920 !important; border-color: #244435 !important; color: #D1FAE5 !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def _render_login_page() -> None:
    col_art, col_form = st.columns([1.05, 1.0], gap="large")

    with col_art:
        logo_svg = (ASSETS_DIR / "logo" / "medileaf_logo.svg").read_text(encoding="utf-8")
        st.markdown(
            f"""
            <div class="medileaf-hero animate-enter" style="min-height: 540px; display:flex; flex-direction:column; justify-content:space-between;">
              <div>
                <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.5rem;">
                  <div style="width:44px; height:44px;">{logo_svg}</div>
                  <div>
                    <div style="font-size:1.2rem; font-weight:800; color:#FFFFFF;">MediLeaf <span class="lime-accent">AI</span></div>
                    <div style="font-size:0.78rem; color:#B7DFC6;">Medicinal Leaf Identifier</div>
                  </div>
                </div>
                <h1 style="font-size:2.2rem; font-weight:800; line-height:1.18;">
                  Medicinal-Leaf Identifier with a <span class="lime-accent">Reject Option</span>
                </h1>
                <p style="color:#E2F5E9; font-size:0.95rem; line-height:1.65; margin-top:1rem;">
                  Fine-tuned PyTorch ResNet50 classification with validation-calibrated confidence &amp; energy gating
                  so unfamiliar species return <strong style="color:#F4B740;">UNCERTAIN</strong> instead of forced guesses.
                </p>
              </div>
              <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.16); border-radius:12px; padding:0.9rem 1rem; font-size:0.8rem; color:#DCFCE7; margin-top:1.5rem;">
                {SAFETY_DISCLAIMER}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_form:
        st.markdown('<div class="medileaf-card animate-enter">', unsafe_allow_html=True)
        st.markdown("### MediLeaf AI")
        st.caption("Discover Nature. Identify Leaves. Understand with Confidence.")
        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            with st.form("medileaf_login_form", clear_on_submit=False):
                identifier = st.text_input("Email or Username", placeholder="Enter your email or username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                remember = st.checkbox("Remember me", value=True)
                submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

            with st.expander("Forgot password?"):
                st.caption(
                    "Credentials are stored locally in SQLite using PBKDF2-HMAC-SHA256. "
                    "Use the Register tab to create a new local account, or change your password under Settings & Help once signed in."
                )
            st.caption("Local PBKDF2-HMAC-SHA256 authentication · No hardcoded credentials")
            if submitted:
                with st.spinner("Verifying credentials..."):
                    ok, msg, user = authenticate_user(identifier, password)
                if ok and user is not None:
                    st.session_state["user"] = user
                    st.session_state["remember_me"] = remember
                    st.session_state["active_page"] = "Home"
                    st.rerun()
                else:
                    st.error(msg)

        with tab_register:
            with st.form("medileaf_register_form", clear_on_submit=True):
                reg_user = st.text_input("Username", placeholder="At least 3 characters")
                reg_email = st.text_input("Email Address", placeholder="you@university.edu")
                reg_pw = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
                reg_pw2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                reg_submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if reg_submit:
                if reg_pw != reg_pw2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg, user = register_user(reg_user, reg_email, reg_pw)
                    if ok and user is not None:
                        st.success(f"{msg} Signing you in...")
                        st.session_state["user"] = user
                        st.session_state["active_page"] = "Home"
                        st.rerun()
                    else:
                        st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_sidebar(user: dict) -> str:
    nav_items = [
        ("Home", "🏠  Dashboard"),
        ("Leaf Identification", "🍃  Leaf Identification"),
        ("Prediction History", "🕘  Prediction History"),
        ("Model Analytics", "📊  Model Analytics"),
        ("Dataset & Information", "📚  Dataset & Information"),
        ("Settings & Help", "⚙️  Settings & Help"),
    ]
    current = st.session_state.get("active_page", "Home")

    with st.sidebar:
        logo_svg = (ASSETS_DIR / "logo" / "medileaf_logo.svg").read_text(encoding="utf-8")
        st.markdown(
            f"""
            <div style="text-align:center; padding:0.4rem 0 1.25rem 0;">
              <div style="width:46px; height:46px; margin:0 auto 0.5rem auto;">{logo_svg}</div>
              <div style="font-size:1.25rem; font-weight:800; color:#FFFFFF;">MediLeaf <span style="color:#9AE66E;">AI</span></div>
              <div style="font-size:0.76rem; color:#B7DFC6;">Medicinal Leaf Identifier</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for key, label in nav_items:
            is_active = current == key or (current == "Prediction Results" and key == "Leaf Identification")
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{key}", type=btn_type, use_container_width=True):
                st.session_state["active_page"] = key
                st.rerun()

        st.markdown("---")
        st.caption(f"Signed in as **{user['username']}**")
        if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    return st.session_state.get("active_page", "Home")


def main() -> None:
    init_db()

    user = st.session_state.get("user")
    if user is None:
        _load_css("Light")
        _render_login_page()
        return

    prefs = get_user_preferences(user["id"])
    st.session_state["preferences"] = prefs
    _load_css(prefs.get("theme", "Light"))
    active_page = _render_sidebar(user)

    if active_page == "Home":
        dashboard.render(user)
    elif active_page in ("Leaf Identification", "Prediction Results"):
        identify_leaf.render(user, prefs)
    elif active_page == "Prediction History":
        prediction_history.render(user)
    elif active_page == "Model Analytics":
        model_analytics.render()
    elif active_page == "Dataset & Information":
        dataset_information.render()
        about.render()
    elif active_page == "Settings & Help":
        settings.render(user, prefs)
    else:
        dashboard.render(user)


if __name__ == "__main__":
    main()
