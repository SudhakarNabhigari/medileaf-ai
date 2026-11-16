"""Page 2 — Home / Dashboard with Interactive Computer Vision Architecture & Technologies."""

from __future__ import annotations

import json
from typing import Dict

import streamlit as st

from auth.authentication import get_prediction_history
from src.config import (
    CHECKPOINT_PATH,
    CLASS_MAPPING_PATH,
    DATASET_REPORTS_DIR,
    MODEL_METADATA_PATH,
    SAFETY_DISCLAIMER,
)
from src.cv_technologies import CVTechnologyCard, get_cv_technologies


def _load_json_safe(path) -> Dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


@st.dialog("Computer Vision Technology Details", width="large")
def _show_tech_dialog(tech: CVTechnologyCard) -> None:
    st.markdown(f"### {tech.short_title} — {tech.full_name}")
    st.caption(f"Category: {tech.category} · Status: **{tech.status}** ({tech.status_detail})")
    st.markdown(f"**What is this?**\n\n{tech.what_is_this}")
    st.markdown(f"**Why do we use it?**\n\n{tech.why_used}")
    st.markdown(f"**How does it work in general?**\n\n{tech.how_it_works}")
    st.markdown(f"**Where do we use it in MEDILEAF.AI?**\n\n{tech.where_used_in_medileaf}")
    st.markdown(f"**Which file or module implements it?**\n\n`{tech.module_path}`")
    st.markdown(f"**What happens when it runs?**\n\n{tech.what_happens_when_runs}")


def render(user: dict) -> None:
    st.markdown("## 🌿 Dashboard")

    st.markdown(
        """
        <div class="medileaf-hero animate-enter">
          <div style="font-size:0.82rem; font-weight:600; color:#DCFCE7; margin-bottom:0.35rem;">
            Computer Vision · ResNet50 · OOD Detection
          </div>
          <h1 style="font-size:2.1rem; font-weight:800;">
            Welcome to <span class="lime-accent">MediLeaf AI</span>
          </h1>
          <p style="margin:0.35rem 0 0 0; color:#E2F5E9; font-size:0.98rem;">
            An Intelligent Medicinal Leaf Identification System with a Reject Option
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    dataset_meta = _load_json_safe(DATASET_REPORTS_DIR / "dataset_metadata.json")
    class_map = _load_json_safe(CLASS_MAPPING_PATH)
    model_meta = _load_json_safe(MODEL_METADATA_PATH)

    known_species_val = (
        str(class_map.get("num_classes"))
        if class_map.get("num_classes") is not None
        else (str(dataset_meta.get("valid_species_count")) if dataset_meta.get("valid_species_count") is not None else "Not Loaded")
    )
    total_images_val = (
        f"{int(dataset_meta['valid_image_count']):,}"
        if dataset_meta.get("valid_image_count") is not None
        else "Not Loaded"
    )
    model_ready = CHECKPOINT_PATH.exists() and model_meta.get("status") == "READY"
    model_status_val = "Ready" if model_ready else "Training Pending"

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, known_species_val, "Known Species", "Run inspect_dataset.py" if known_species_val == "Not Loaded" else "Verified in split"),
        (c2, total_images_val, "Total Images", "Mendeley v3 archive"),
        (c3, "ResNet50", "Model", "PyTorch Transfer Learning"),
        (c4, model_status_val, "Model Status", "Checkpoint loaded" if model_ready else "Awaiting best_model.pth"),
    ]
    for col, val, label, sub in cards:
        with col:
            st.markdown(
                f"""
                <div class="medileaf-card animate-enter">
                  <div class="medileaf-metric-label">{label}</div>
                  <div class="medileaf-metric-val">{val}</div>
                  <div style="font-size:0.75rem; color:#68796F; margin-top:0.2rem;">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.05, 1.0], gap="large")

    with left:
        st.markdown('<div class="medileaf-card">', unsafe_allow_html=True)
        st.subheader("⚡ Quick Actions")
        qa1, qa2, qa3 = st.columns(3)
        with qa1:
            if st.button("🍃 Identify Leaf", type="primary", use_container_width=True):
                st.session_state["active_page"] = "Leaf Identification"
                st.rerun()
        with qa2:
            if st.button("📊 View Analytics", use_container_width=True):
                st.session_state["active_page"] = "Model Analytics"
                st.rerun()
        with qa3:
            if st.button("📚 Dataset Info", use_container_width=True):
                st.session_state["active_page"] = "Dataset & Information"
                st.rerun()
        st.markdown(
            f"<div class='medileaf-disclaimer' style='margin-top:0.9rem;'>{SAFETY_DISCLAIMER}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="medileaf-card">', unsafe_allow_html=True)
        st.subheader("🕘 Recent Activity")
        history = get_prediction_history(user["id"], limit=5)
        if not history:
            st.info("No predictions yet. Upload a leaf image on the Leaf Identification page after training.")
        else:
            for item in history:
                conf_txt = f"{item['confidence']*100:.1f}%" if item["confidence"] is not None else "—"
                st.markdown(
                    f"**{item['predicted_species']}** · Confidence: `{conf_txt}` · Status: `{item['status']}` · {item['created_at']}"
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # Interactive Computer Vision Architecture & Technologies Section
    st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 🧠 Computer Vision Architecture & Technologies")
    st.caption("Click any technology card below to inspect how it works, where it is used in MEDILEAF.AI, its source module, and its verified execution status.")

    tech_list = get_cv_technologies()
    for row_start in range(0, len(tech_list), 3):
        cols = st.columns(3, gap="medium")
        for col, tech in zip(cols, tech_list[row_start : row_start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="medileaf-card" style="margin-bottom:0.4rem;">
                      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
                        <strong style="color:#053821; font-size:1rem;">{tech.short_title}</strong>
                        <span style="font-size:0.72rem; font-weight:700; color:{'#13823D' if tech.status=='VERIFIED' else '#B45309' if tech.status=='IMPLEMENTED' else '#68796F'};">{tech.status}</span>
                      </div>
                      <div style="font-size:0.8rem; font-weight:600; color:#18352A;">{tech.full_name}</div>
                      <p style="font-size:0.78rem; color:#68796F; margin:0.35rem 0 0 0;">{tech.summary}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Inspect {tech.short_title} →", key=f"tech_{tech.key}", use_container_width=True):
                    _show_tech_dialog(tech)
