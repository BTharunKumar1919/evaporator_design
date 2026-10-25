"""Render results, equipment-specific calculations, checks and report downloads."""
from __future__ import annotations
import json
import pandas as pd
import streamlit as st
from reporting.report_generator import result_to_text, result_to_csv


def _metric_value(value, scale=1.0, suffix="", digits=3):
    if value is None:
        return "N/A"
    return f"{float(value) / scale:.{digits}f}{suffix}"


def _flatten_for_table(obj, prefix=""):
    rows = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            label = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, dict):
                rows.extend(_flatten_for_table(value, label))
            elif isinstance(value, list):
                rows.append({"Parameter": label, "Value": " | ".join(map(str, value))})
            else:
                rows.append({"Parameter": label, "Value": value})
    return rows


def render_results(result: dict, process_inputs: dict, geometry: dict) -> None:
    st.header("Calculation results")
    st.caption("Course-algorithm implementation for preliminary design/rating. The output flags missing correlation inputs and failed checks; it is not a certified mechanical or process design.")
    if result.get("errors"):
        st.error("The calculation could not proceed because of input errors.")
        for e in result["errors"]:
            st.write(f"- {e}")
        return

    st.subheader(f"{result.get('mode')} · {result.get('exchanger')}")
    st.info(f"Calculation status: **{result.get('status', 'PRELIMINARY RESULT')}**")
    if result.get("mode") == "Sizing":
        cols = st.columns(4)
        cols[0].metric("Process duty", _metric_value(result.get("required_duty_W"), 1000, " kW"))
        cols[1].metric("Sizing duty", _metric_value(result.get("design_duty_W"), 1000, " kW"))
        cols[2].metric("Required area", _metric_value(result.get("required_area_m2"), 1, " m²"))
        cols[3].metric("Calculated tube count", str(result.get("tube_count_required", "N/A")))
        cols = st.columns(4)
        cols[0].metric("Installed area", _metric_value(result.get("installed_area_m2"), 1, " m²"))
        cols[1].metric("Calculated capacity", _metric_value(result.get("predicted_capacity_W"), 1000, " kW"))
        cols[2].metric("Effective ΔT", _metric_value((result.get("thermal") or {}).get("effective_temperature_difference_K"), 1, " K"))
        cols[3].metric("Installed / required area", _metric_value(result.get("capacity_ratio"), 1, "×"))
        if result.get("recommended_geometry"):
            with st.expander("Recommended preliminary geometry", expanded=True):
                st.dataframe(pd.DataFrame([{"Parameter": k, "Value": v} for k, v in result["recommended_geometry"].items()]), use_container_width=True, hide_index=True)
        area_req, area_installed = result.get("required_area_m2"), result.get("installed_area_m2")
        if area_req and area_installed:
            st.subheader("Area comparison")
            st.bar_chart(pd.DataFrame({"Area (m²)": [area_req, area_installed]}, index=["Required", "Installed"]))
    else:
        cols = st.columns(4)
        cols[0].metric("Available area", _metric_value(result.get("available_area_m2"), 1, " m²"))
        cols[1].metric("Calculated thermal capacity", _metric_value(result.get("capacity_W"), 1000, " kW"))
        cols[2].metric("Target duty", _metric_value(result.get("target_duty_W"), 1000, " kW"))
        cols[3].metric("Capacity / target duty", _metric_value(result.get("capacity_ratio"), 1, "×"))
        cols = st.columns(3)
        cols[0].metric("Target vapor fraction", _metric_value(result.get("target_vapor_fraction"), 1, "", 2))
        cols[1].metric("Estimated achievable fraction", _metric_value(result.get("achieved_vapor_fraction"), 1, "", 2))
        cols[2].metric("Effective ΔT", _metric_value((result.get("thermal") or {}).get("effective_temperature_difference_K"), 1, " K"))

    if result.get("engineering_calculations"):
        st.subheader("Equipment-specific algorithm results")
        st.caption("The parameter names follow the supplied algorithms: HTC/resistance network, natural-circulation balance, CHF, Palen dry-out, distributor and disengagement screens as relevant to the selected equipment.")
        rows = _flatten_for_table(result["engineering_calculations"])
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if result.get("preliminary_checks"):
        st.subheader("Decision gates")
        st.dataframe(pd.DataFrame(_flatten_for_table(result["preliminary_checks"])), use_container_width=True, hide_index=True)

    st.subheader("Pressure-drop estimates")
    st.caption("A generic single-phase result is not presented as a validated two-phase pressure drop. Natural-circulation/boiling drops remain unknown unless a justified loop-loss estimate is supplied.")
    p1, p2 = st.columns(2)
    for col, key, title in [(p1, "process_dp", "Process side / circulation loop"), (p2, "hot_dp", "Heating side")]:
        dp = result.get(key) or {}
        with col:
            st.markdown(f"**{title}**")
            if dp.get("delta_p_kPa") is None:
                st.write(dp.get("status", "Not calculated"))
            else:
                st.metric("Estimated ΔP", f"{dp['delta_p_kPa']:.4g} kPa")
                if dp.get("velocity_m_s") is not None:
                    st.write(f"Velocity: {_metric_value(dp.get('velocity_m_s'), 1, ' m/s')}")
                if dp.get("Reynolds") is not None:
                    st.write(f"Reynolds number: {_metric_value(dp.get('Reynolds'), 1, '')}")
                st.caption(str(dp.get("status", "")))

    st.subheader("Thermal calculation basis")
    thermal = result.get("thermal") or {}
    if thermal:
        st.dataframe(pd.DataFrame(_flatten_for_table(thermal)), use_container_width=True, hide_index=True)

    with st.expander("Calculation trace", expanded=False):
        for step in result.get("calculation_trace", []):
            st.code(step, language="text")
    with st.expander("Inputs used", expanded=False):
        st.markdown("**Process and property inputs**")
        st.dataframe(pd.DataFrame([{"Parameter": k, "Value": v} for k, v in process_inputs.items()]), use_container_width=True, hide_index=True)
        st.markdown("**Geometry inputs**")
        st.dataframe(pd.DataFrame([{"Parameter": k, "Value": v} for k, v in geometry.items()]), use_container_width=True, hide_index=True)

    warnings = list(result.get("warnings") or []) + list(result.get("model_notes") or [])
    warnings = list(dict.fromkeys(warnings))
    if warnings:
        st.subheader("Warnings and limitations")
        for warning in warnings:
            st.warning(warning)

    report_text = result_to_text(result, process_inputs, geometry)
    st.download_button("Download calculation report", data=report_text, file_name="evaporator_preliminary_report.txt", mime="text/plain")
    st.download_button("Download result CSV", data=result_to_csv(result), file_name="evaporator_preliminary_results.csv", mime="text/csv")
