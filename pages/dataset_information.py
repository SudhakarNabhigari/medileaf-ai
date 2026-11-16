"""Page 7 — Dataset & Information view backed by verified Mendeley metadata and real inventory."""

from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import streamlit as st

from src.config import DATASET_REPORTS_DIR, ROOT_DIR, SPLIT_CONFIG_PATH, VERIFIED_DATASET_METADATA


def render() -> None:
    st.markdown("## 📚 Dataset & Information")
    st.caption("Explore the dataset details, class distribution, and project information")

    st.markdown(
        """
        <div class="medileaf-hero animate-enter">
          <h1 style="font-size:1.85rem; font-weight:800; margin:0;">
            Dataset &amp; <span class="lime-accent">Project Information</span>
          </h1>
          <p style="margin:0.35rem 0 0 0; color:#E2F5E9; font-size:0.94rem;">
            Verified details of the Indian Medicinal Leaves Image Datasets (Mendeley v3), class distribution, and academic scope.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    meta_path = DATASET_REPORTS_DIR / "dataset_metadata.json"
    dist_path = DATASET_REPORTS_DIR / "class_distribution.csv"
    dataset_meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    split_cfg = json.loads(SPLIT_CONFIG_PATH.read_text(encoding="utf-8")) if SPLIT_CONFIG_PATH.exists() else {}

    col_details, col_dist = st.columns([1.05, 1.15], gap="large")

    with col_details:
        st.markdown('<div class="medileaf-card">', unsafe_allow_html=True)
        st.subheader("Dataset Details")
        total_images = f"{int(dataset_meta['valid_image_count']):,}" if dataset_meta.get("valid_image_count") else "Dataset not loaded"
        total_species = str(dataset_meta["valid_species_count"]) if dataset_meta.get("valid_species_count") else "Dataset not loaded"
        rows = [
            ("Dataset Name", VERIFIED_DATASET_METADATA["dataset_name"]),
            ("Source", VERIFIED_DATASET_METADATA["source"]),
            ("Version", VERIFIED_DATASET_METADATA["version"]),
            ("DOI", VERIFIED_DATASET_METADATA["doi"]),
            ("Licence", VERIFIED_DATASET_METADATA["licence"]),
            ("Contributors", VERIFIED_DATASET_METADATA["contributors"]),
            ("Total Images", total_images),
            ("Total Species", total_species),
            ("Poisonous Coverage", VERIFIED_DATASET_METADATA["poisonous_coverage_status"]),
        ]
        for k, v in rows:
            st.markdown(f"**{k}:** {v}")
        if split_cfg:
            st.caption(
                f"Split Counts — Train: {split_cfg['counts']['train']} · Val: {split_cfg['counts']['validation']} "
                f"· Known Test: {split_cfg['counts']['known_test']} · Held-Out OOD: {split_cfg['counts']['ood_test']}"
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_dist:
        st.markdown('<div class="medileaf-card">', unsafe_allow_html=True)
        st.subheader("Class Distribution (Top 5)")
        if dist_path.exists():
            dist_df = pd.read_csv(dist_path).head(5)
            st.bar_chart(dist_df.set_index("species")["valid_image_count"])
        else:
            st.info("Dataset not loaded. Extract the Mendeley v3 archive into `data/raw/` and inspect verified species counts.")
            if st.button("Load & Analyze Dataset", type="primary", use_container_width=True):
                proc = subprocess.run(
                    [sys.executable, "scripts/inspect_dataset.py"],
                    cwd=str(ROOT_DIR),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if proc.returncode == 0:
                    st.success("Dataset audit completed! Refreshing...")
                    st.rerun()
                else:
                    st.error((proc.stderr or proc.stdout or "Dataset inspection failed.").strip())
        st.markdown("</div>", unsafe_allow_html=True)
