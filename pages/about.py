"""About MEDILEAF.AI section rendered inside Dataset & Information."""

from __future__ import annotations

import streamlit as st

from src.config import SAFETY_DISCLAIMER


def render() -> None:
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="medileaf-card">
          <h3 style="margin-top:0; color:#064E32;">About the Project</h3>
          <p style="color:#18352A; line-height:1.65;">
            <strong>MEDILEAF.AI</strong> (<em>Medicinal-Leaf Identifier with a Reject Option</em>) is an academic
            Computer Vision system that identifies supported plant species from leaf photographs using a fine-tuned
            PyTorch ResNet50 Convolutional Neural Network and returns <strong>UNCERTAIN</strong> for unfamiliar
            (out-of-distribution) or low-reliability inputs.
          </p>
          <div class="medileaf-disclaimer">{SAFETY_DISCLAIMER}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
