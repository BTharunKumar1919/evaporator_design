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
st.write("A preliminary design and rating tool for five evaporator/reboiler types. It follows the uploaded course algorithms where equations and inputs are reproducible, reports equipment-specific checks, and flags correlations or hydraulic calculations that need engineering review.")

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
    st.caption("The recommender applies the uploaded priority gates, calculates pre-processing quantities, then ranks candidates. You can select any exchanger in the next step; the recommendation is not a final engineering approval.")
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
    st.markdown("### Pre-processing calculations")
    prep = recommend_equipment.last_preprocessing
    pc1, pc2, pc3 = st.columns(3)
    pc1.metric("Estimated heat duty", f"{prep.get('total_duty_kW', 0):,.2f} kW")
    pc2.metric("Exit vapor fraction xe", f"{prep.get('exit_vapor_fraction_xe', 0):.3f}")
    pc3.metric("Static head", f"{prep.get('available_static_head_kPa', 0):.2f} kPa")
    st.write(f"Recirculation ratio R: **{prep.get('recirculation_ratio_R') if prep.get('recirculation_ratio_R') is not None else 'undefined at xe = 0'}**")
    st.write(f"Effective temperature approach ΔTeff: **{prep.get('effective_temperature_approach_C', 0):.2f} °C**")
    with st.expander("Show priority-gate trace"):
        for line in recommend_equipment.last_trace:
            st.write("- " + line)
    st.markdown("### Ranked equipment candidates")
    st.caption("The score orders candidates using the uploaded priority gates and secondary preferences. ‘Review required’ means a gate/constraint cautions against that option; this is not a certified hard rejection. You remain free to select any type, but review its cautions first.")
    rank_df = pd.DataFrame([{
        "Rank": r["rank"], "Exchanger": r["exchanger"], "Score": r["score"],
        "Status": r["status"], "Why ranked here": "; ".join(r["reasons"]),
        "Cautions": "; ".join(r["cautions"]),
    } for r in rankings])
    st.dataframe(rank_df, use_container_width=True, hide_index=True)
    rank_options = [r["exchanger"] for r in rankings]
    with st.form("sizing_geometry_form"):
        exchanger = st.selectbox("Select exchanger module", rank_options, index=0,
                                 format_func=lambda name: f"{name} — rank #{next(r['rank'] for r in rankings if r['exchanger'] == name)}",
                                 help="The highest-ranked type is preselected, but you can choose any of the five types. Review cautions before overriding a priority gate.")
        selected_row = next(r for r in rankings if r["exchanger"] == exchanger)
        st.info(f"Selected: {exchanger}. Tube side: {selected_row['tube_side']}. Shell side: {selected_row['shell_side']}.")
        if selected_row["cautions"]:
            st.warning("Selection cautions: " + " ".join(selected_row["cautions"]))
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
