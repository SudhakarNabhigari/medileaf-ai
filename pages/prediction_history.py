"""Page 5 — Prediction History for MEDILEAF.AI."""

from __future__ import annotations

import streamlit as st

from auth.authentication import clear_prediction_history, get_prediction_history


def render(user: dict) -> None:
    head_left, head_right = st.columns([3.2, 1.0])
    with head_left:
        st.markdown("## 🕘 Prediction History")
        st.caption("View and manage your past leaf identification results")
    with head_right:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state["confirm_clear_history"] = True

    st.markdown(
        """
        <div class="medileaf-hero animate-enter">
          <h1 style="font-size:1.85rem; font-weight:800; margin:0;">
            Your <span class="lime-accent">Prediction History</span>
          </h1>
          <p style="margin:0.35rem 0 0 0; color:#E2F5E9; font-size:0.94rem;">
            All your leaf identification attempts are stored here with predicted species, confidence scores, and results.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("confirm_clear_history"):
        st.warning("Are you sure you want to permanently delete your saved prediction history?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Confirm Clear", type="primary", use_container_width=True):
                clear_prediction_history(user["id"])
                st.session_state["confirm_clear_history"] = False
                st.rerun()
        with c2:
            if st.button("Cancel", use_container_width=True):
                st.session_state["confirm_clear_history"] = False
                st.rerun()

    records = get_prediction_history(user["id"], limit=200)
    total_cnt = len(records)
    accepted_cnt = sum(1 for r in records if r["status"] == "Accepted")
    rejected_cnt = sum(1 for r in records if r["status"] != "Accepted")
    last_time = records[0]["created_at"] if records else "--"

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, str(total_cnt), "Total Predictions"),
        (k2, str(accepted_cnt), "Known (Accepted)"),
        (k3, str(rejected_cnt), "Uncertain (Rejected)"),
        (k4, str(last_time), "Last Prediction"),
    ]
    for col, val, label in kpis:
        with col:
            st.markdown(
                f"""
                <div class="medileaf-card animate-enter">
                  <div class="medileaf-metric-label">{label}</div>
                  <div class="medileaf-metric-val" style="font-size:{'1.1rem' if label=='Last Prediction' else '1.55rem'};">{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    f_col1, f_col2 = st.columns([1.0, 2.0])
    with f_col1:
        status_filter = st.selectbox("Filter Status", ["All Results", "Accepted", "Rejected"])
    with f_col2:
        search_q = st.text_input("Search by species", placeholder="Search by species...")

    filtered = [
        r
        for r in records
        if (status_filter == "All Results" or r["status"] == status_filter)
        and (not search_q.strip() or search_q.strip().lower() in (r["predicted_species"] or "").lower())
    ]

    if not filtered:
        st.info("No predictions yet. Upload a leaf on the Leaf Identification page after model training to record real predictions here.")
        if st.button("🍃 Identify a Leaf →", type="primary"):
            st.session_state["active_page"] = "Leaf Identification"
            st.rerun()
        return

    for idx, rec in enumerate(filtered, start=1):
        with st.container():
            cols = st.columns([0.5, 1.0, 2.5, 1.2, 1.2, 1.8])
            cols[0].write(f"**{idx}**")
            if rec.get("image_thumbnail_b64"):
                cols[1].markdown(
                    f'<img src="data:image/jpeg;base64,{rec["image_thumbnail_b64"]}" width="48" style="border-radius:8px;" />',
                    unsafe_allow_html=True,
                )
            else:
                cols[1].write("—")
            cols[2].write(f"**{rec['predicted_species']}**")
            cols[3].write(f"`{rec['confidence']:.2f}`" if rec["confidence"] is not None else "—")
            cols[4].write("Accepted" if rec["status"] == "Accepted" else "Rejected")
            cols[5].write(rec["created_at"])
        st.divider()
