"""Page 8 — Settings & Help for MEDILEAF.AI."""

from __future__ import annotations

import streamlit as st

from auth.authentication import change_password, update_user_preferences
from src.config import SAFETY_DISCLAIMER


def render(user: dict, prefs: dict) -> None:
    st.markdown("## ⚙️ Settings & Help")
    tab_settings, tab_help = st.tabs(["Settings", "Help & Support"])

    with tab_settings:
        col_left, col_right = st.columns([1.1, 1.0], gap="large")
        with col_left:
            st.markdown('<div class="medileaf-card">', unsafe_allow_html=True)
            st.subheader("Application Preferences")
            theme = st.radio(
                "App Theme",
                options=["Light", "Dark", "System"],
                index=["Light", "Dark", "System"].index(prefs.get("theme", "Light")),
                horizontal=True,
            )
            notif = st.toggle("Notifications", value=bool(prefs.get("notifications_enabled", True)))
            save_hist = st.toggle("Save Prediction History", value=bool(prefs.get("save_history_enabled", True)))

            if st.button("Save Preferences", type="primary"):
                update_user_preferences(user["id"], theme, notif, save_hist)
                st.session_state["preferences"] = {
                    "theme": theme,
                    "notifications_enabled": notif,
                    "save_history_enabled": save_hist,
                }
                st.success("Preferences saved.")

            st.markdown("---")
            st.subheader("Account")
            with st.expander("Change Password"):
                curr_pw = st.text_input("Current Password", type="password")
                new_pw = st.text_input("New Password", type="password")
                if st.button("Update Password"):
                    ok, msg = change_password(user["id"], curr_pw, new_pw)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

            if st.button("Logout", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            _render_help_panel()

    with tab_help:
        _render_help_panel()


def _render_help_panel() -> None:
    st.markdown('<div class="medileaf-card">', unsafe_allow_html=True)
    st.subheader("Need Help?")
    with st.expander("How to get better results?", expanded=True):
        st.write(
            "Use a sharp, well-lit photograph showing a single medicinal plant leaf against a plain or natural "
            "background without heavy motion blur or extreme occlusion."
        )
    with st.expander("Supported image formats"):
        st.write("JPG, JPEG, and PNG images up to 10 MB (minimum resolution 32×32 px; resized and center-cropped to 224×224 for ResNet50).")
    with st.expander("Understanding 'UNCERTAIN'"):
        st.write(
            "When maximum softmax confidence falls below the validation-calibrated threshold or the energy-based OOD score "
            "exceeds the in-distribution boundary, MEDILEAF.AI abstains and outputs UNCERTAIN rather than guessing."
        )
    with st.expander("Dataset and model information"):
        st.write(
            "ResNet50 pretrained on ImageNet (`IMAGENET1K_V2`), fine-tuned on known classes from the Mendeley "
            "Indian Medicinal Leaves Image Datasets (Version 3, DOI: 10.17632/748f8jkphb.3) with held-out species isolated for OOD evaluation."
        )
    with st.expander("Safety & academic disclaimer"):
        st.write(SAFETY_DISCLAIMER)
    st.markdown("</div>", unsafe_allow_html=True)
