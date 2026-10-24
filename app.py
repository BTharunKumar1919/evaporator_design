"""Evaporator Design & Rating — Streamlit starter application.

Run with: streamlit run app.py
"""
from __future__ import annotations
import pandas as pd
import streamlit as st

from core.models import EXCHANGERS, DEFAULT_GEOMETRY
from core.equipment_selection import recommend_equipment
from core.solver import calculate
from core.validation import validate_process_inputs, validate_geometry
from ui.forms import process_input_fields, geometry_input_fields
from ui.results import render_results

st.set_page_config(page_title="Evaporator Design & Rating", page_icon="♨️", layout="wide")

if "step" not in st.session_state:
    st.session_state.step = 1
if "mode" not in st.session_state:
    st.session_state.mode = "Sizing"

with st.sidebar:
    st.title("Evaporator tool")
    st.caption("Sizing + Rating starter template")
    st.markdown("---")
    st.markdown("**Workflow**")
    labels = {1: "1. Mode", 2: "2. Process inputs", 3: "3. Equipment selection / geometry", 4: "4. Results"}
    for n in range(1, 5):
        prefix = "▶ " if st.session_state.step == n else "　"
        st.write(prefix + labels[n])
    st.markdown("---")
    st.caption("The physics and pressure-drop models are intentionally preliminary. Do not use results for final design or safety approval.")

st.title("Evaporator Design & Rating")
st.write("A working end-to-end scaffold for five evaporator/reboiler types. Use the default case first to check the workflow; then replace the placeholder correlations with your course-approved methods.")

if st.session_state.step == 1:
    st.header("Step 1 — Choose calculation mode")
    with st.form("mode_form"):
        mode = st.radio("What do you want to do?", ["Sizing", "Rating"], horizontal=True,
                        help="Sizing calculates preliminary geometry from process requirements. Rating estimates performance for an existing geometry.")
        st.markdown("**Sizing:** process requirements → equipment recommendation → exchanger-specific sizing.\n\n**Rating:** exchanger type + operating conditions + existing geometry → performance estimate.")
        submitted = st.form_submit_button("Continue", type="primary")
    if submitted:
        st.session_state.mode = mode
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2 and st.session_state.mode == "Sizing":
    st.header("Step 2 — Enter sizing requirements")
    st.caption("The recommender uses only the qualitative preferences shown here. You can override its ranking in the next step.")
    with st.form("sizing_process_form"):
        process = process_input_fields("szp", include_preferences=True)
        submitted = st.form_submit_button("Validate requirements and continue", type="primary")
    if submitted:
        errors, warnings = validate_process_inputs(process)
        if errors:
            st.error("Please correct the following inputs before continuing:")
            for e in errors:
                st.write(f"- {e}")
        else:
            st.session_state.process_inputs = process
            st.session_state.process_warnings = warnings
            st.session_state.step = 3
            st.rerun()
    if st.button("Back to mode selection"):
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 2 and st.session_state.mode == "Rating":
    st.header("Step 2 — Select exchanger and enter rating inputs")
    st.caption("Rating bypasses the equipment-selection algorithm and goes directly to the exchanger type you select.")
    with st.form("rating_form"):
        exchanger = st.selectbox("Exchanger type", list(EXCHANGERS.keys()))
        process = process_input_fields("rtp", include_preferences=False)
        geometry = geometry_input_fields("rtg", rating=True)
        submitted = st.form_submit_button("Run rating calculation", type="primary")
    if submitted:
        p_errors, p_warnings = validate_process_inputs(process)
        g_errors, g_warnings = validate_geometry(geometry)
        errors = p_errors + g_errors
        if errors:
            st.error("Please correct the following inputs before calculating:")
            for e in errors:
                st.write(f"- {e}")
        else:
            result = calculate("Rating", exchanger, process, geometry)
            st.session_state.process_inputs = process
            st.session_state.geometry = geometry
            st.session_state.exchanger = exchanger
            st.session_state.result = result
            st.session_state.process_warnings = p_warnings + g_warnings
            st.session_state.step = 4
            st.rerun()
    if st.button("Back to mode selection"):
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 3:
    st.header("Step 3 — Equipment selection and preliminary geometry")
    process = st.session_state.process_inputs
    rankings = recommend_equipment(process)
    st.markdown("### Preliminary recommendation ranking")
    st.caption("This transparent rule-based ranking is only a placeholder based on the preferences entered. It does not replace the course flowchart or engineering judgment.")
    rank_df = pd.DataFrame([{
        "Rank": r["rank"], "Exchanger": r["exchanger"], "Heuristic score": r["score"],
        "Reason(s)": "; ".join(r["reasons"]),
    } for r in rankings])
    st.dataframe(rank_df, use_container_width=True, hide_index=True)
    rank_options = [r["exchanger"] for r in rankings]
    with st.form("sizing_geometry_form"):
        exchanger = st.selectbox("Select exchanger module", rank_options, index=0,
                                 help="The highest-ranked type is preselected, but you can choose any of the five types.")
        geometry = geometry_input_fields("szg", rating=False)
        submitted = st.form_submit_button("Run preliminary sizing", type="primary")
    if submitted:
        p_errors, p_warnings = validate_process_inputs(process)
        g_errors, g_warnings = validate_geometry(geometry)
        errors = p_errors + g_errors
        if errors:
            st.error("Please correct the following inputs before calculating:")
            for e in errors:
                st.write(f"- {e}")
        else:
            result = calculate("Sizing", exchanger, process, geometry)
            st.session_state.geometry = geometry
            st.session_state.exchanger = exchanger
            st.session_state.result = result
            st.session_state.process_warnings = p_warnings + g_warnings
            st.session_state.step = 4
            st.rerun()
    if st.button("Back to process requirements"):
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 4:
    result = st.session_state.get("result", {})
    process = st.session_state.get("process_inputs", {})
    geometry = st.session_state.get("geometry", DEFAULT_GEOMETRY)
    render_results(result, process, geometry)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Edit inputs", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Start a new calculation", type="primary", use_container_width=True):
            for key in ["process_inputs", "process_warnings", "geometry", "exchanger", "result"]:
                st.session_state.pop(key, None)
            st.session_state.step = 1
            st.session_state.mode = "Sizing"
            st.rerun()
