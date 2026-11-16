"""Page 3 & Page 4 — Leaf Identification and Prediction Results (Accepted / UNCERTAIN)."""

from __future__ import annotations

import base64
import io

import streamlit as st
from PIL import Image

from auth.authentication import save_prediction_record
from src.config import MAX_UPLOAD_SIZE_BYTES, SAFETY_DISCLAIMER, UI_SUPPORTED_EXTENSIONS
from src.data import validate_image_bytes
from src.inference import MediLeafPredictor


@st.cache_resource(show_spinner=False)
def _get_predictor() -> MediLeafPredictor:
    return MediLeafPredictor()


def _make_thumbnail_b64(img: Image.Image, size: tuple[int, int] = (72, 72)) -> str:
    thumb = img.copy()
    thumb.thumbnail(size)
    buf = io.BytesIO()
    thumb.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def render(user: dict, prefs: dict) -> None:
    st.markdown("## 🍃 Leaf Identification")

    st.markdown(
        """
        <div class="medileaf-hero animate-enter">
          <h1 style="font-size:1.9rem; font-weight:800; margin:0;">
            Identify a <span class="lime-accent">Leaf</span>
          </h1>
          <p style="margin:0.35rem 0 0.75rem 0; color:#E2F5E9; font-size:0.95rem;">
            Upload a leaf image to identify the plant species using our ResNet50 model with a reject option.
          </p>
          <div style="display:flex; gap:1.5rem; flex-wrap:wrap; font-size:0.82rem; color:#DCFCE7;">
            <span><strong style="color:#9AE66E;">CNN</strong> (ResNet50)</span>
            <span>|</span>
            <span><strong style="color:#9AE66E;">Rejects</strong> Unknown (Uncertain)</span>
            <span>|</span>
            <span><strong style="color:#9AE66E;">Accurate</strong> &amp; Reliable</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    predictor = _get_predictor()

    if not predictor.is_ready:
        st.warning(
            f"**Model Training Pending:** {predictor.ready_error}\n\n"
            "Upload validation still works below, and predictions will execute automatically once "
            "`artifacts/best_model.pth`, `artifacts/class_mapping.json`, and `artifacts/rejection_config.json` are generated."
        )

    uploaded = st.file_uploader(
        "Upload a Leaf Image (JPG, JPEG, PNG | Max size: 10 MB)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
    )

    if uploaded is None:
        st.info("Drag and drop a clear leaf photograph above or click Browse files to begin.")
    else:
        raw_bytes = uploaded.getvalue()
        validation = validate_image_bytes(
            raw_bytes,
            filename=uploaded.name,
            allowed_extensions=UI_SUPPORTED_EXTENSIONS,
            max_size_bytes=MAX_UPLOAD_SIZE_BYTES,
        )

        if not validation.is_valid or validation.image is None:
            st.error(validation.error_message or "Uploaded file failed image validation.")
        else:
            col_preview, col_action = st.columns([1.0, 1.3], gap="large")
            with col_preview:
                st.image(
                    validation.image,
                    caption=f"{uploaded.name} ({validation.width}×{validation.height}px)",
                    use_container_width=True,
                )

            with col_action:
                st.markdown('<div class="medileaf-card">', unsafe_allow_html=True)
                st.markdown(f"**File:** `{uploaded.name}`")
                st.markdown(
                    f"**Dimensions:** `{validation.width} × {validation.height} px` · **Mode:** `{validation.mode}`"
                )
                st.markdown(f"**Size:** `{validation.file_size_bytes / 1024:.1f} KB`")
                predict_clicked = st.button("Predict Species →", type="primary", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if predict_clicked:
                with st.spinner("Running ResNet50 preprocessing, forward pass, and confidence gate..."):
                    result = predictor.predict_bytes(
                        raw_bytes,
                        filename=uploaded.name,
                        allowed_extensions=UI_SUPPORTED_EXTENSIONS,
                    )
                st.session_state["last_prediction"] = result.to_dict()
                st.session_state["last_prediction_image"] = raw_bytes

                if prefs.get("save_history_enabled", True) and result.status in ("ACCEPTED", "UNCERTAIN"):
                    thumb_b64 = _make_thumbnail_b64(validation.image)
                    save_prediction_record(
                        user_id=user["id"],
                        filename=uploaded.name,
                        predicted_species=result.predicted_species,
                        confidence=result.confidence,
                        energy_score=result.energy_score,
                        status="Accepted" if result.accepted else "Rejected",
                        reason=result.reason,
                        image_thumbnail_b64=thumb_b64,
                    )

    last_res = st.session_state.get("last_prediction")
    if last_res:
        st.markdown("---")
        st.markdown("### Prediction Results")

        if last_res["status"] == "MODEL_NOT_READY":
            st.warning(f"**Model Training Pending:** {last_res['reason']}")
        elif last_res["status"] == "INVALID_IMAGE":
            st.error(last_res["reason"])
        else:
            conf = float(last_res["confidence"] or 0.0)
            if last_res["accepted"]:
                st.markdown(
                    f"""
                    <div class="medileaf-accepted-box animate-enter">
                      <div style="color:#13823D; font-weight:700; font-size:0.95rem;">✓ Prediction Accepted</div>
                      <h2 style="color:#064E32; margin:0.25rem 0;">{last_res['predicted_species']}</h2>
                      <div style="font-family:'JetBrains Mono',monospace; font-size:1.05rem; color:#18352A;">
                        Confidence: {conf:.2f} ({conf*100:.1f}%) · Energy Score: {last_res['energy_score']:.3f}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(max(conf, 0.0), 1.0))

                st.markdown(
                    f"""
                    <div class="medileaf-card" style="margin-top:1rem;">
                      <h4 style="margin-top:0; color:#064E32;">Verified Classification Details</h4>
                      <p><strong>Predicted Dataset Class:</strong> {last_res['predicted_species']}</p>
                      <p><strong>Decision Rule:</strong> {last_res['reason']}</p>
                      <div class="medileaf-disclaimer">{SAFETY_DISCLAIMER}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="medileaf-uncertain-box animate-enter">
                      <div style="color:#B45309; font-weight:800; font-size:1.1rem;">⚠ UNCERTAIN</div>
                      <p style="color:#18352A; font-weight:600; margin:0.35rem 0;">
                        The model cannot confidently identify this leaf.
                      </p>
                      <div style="font-family:'JetBrains Mono',monospace; font-size:0.98rem; color:#465B50;">
                        Max Confidence: {conf:.2f} ({conf*100:.1f}%) · Threshold: {last_res['threshold_used']:.2f} · Energy: {last_res['energy_score']:.3f}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(max(conf, 0.0), 1.0))

                st.markdown(
                    f"""
                    <div class="medileaf-card" style="margin-top:1rem;">
                      <h4 style="margin-top:0; color:#92400E;">Why UNCERTAIN?</h4>
                      <ul>
                        <li>{last_res['reason']}</li>
                        <li>The leaf may belong to a species not seen during training (out-of-distribution).</li>
                        <li>Try uploading a sharper, well-lit photograph focused on a single leaf.</li>
                      </ul>
                      <div class="medileaf-disclaimer">{SAFETY_DISCLAIMER}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    feature_cards = [
        (f1, "Plant Identification", "Detects known medicinal leaves"),
        (f2, "Uncertainty Handling", 'Returns "UNCERTAIN" for unfamiliar leaves'),
        (f3, "Model", "ResNet50 (Transfer Learning)"),
        (f4, "Dataset", "Indian Medicinal Leaf Dataset (Mendeley)"),
    ]
    for col, title, desc in feature_cards:
        with col:
            st.markdown(
                f"""
                <div class="medileaf-card" style="padding:0.95rem 1.05rem;">
                  <div style="font-weight:700; font-size:0.86rem; color:#053821;">{title}</div>
                  <div style="font-size:0.78rem; color:#68796F; margin-top:0.2rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
