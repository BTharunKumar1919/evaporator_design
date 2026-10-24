"""Render results, calculation traces, and download links in Streamlit."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from reporting.report_generator import result_to_text, result_to_csv


def _metric_value(value, scale=1.0, suffix="", digits=3):
    if value is None:
        return "N/A"
    return f"{float(value) / scale:.{digits}f}{suffix}"


def render_results(result: dict, process_inputs: dict, geometry: dict) -> None:
    st.header("Calculation results")
    st.caption("Preliminary estimates only — the model limitations below are part of the result, not optional fine print.")
    if result.get("errors"):
        st.error("The calculation could not proceed because of input errors.")
        for item in result["errors"]:
            st.write(f"- {item}")
        return

    st.subheader(f"{result.get('mode')} · {result.get('exchanger')}")
    status = result.get("status", "PRELIMINARY RESULT")
    st.info(f"Calculation status: **{status}**")

    if result.get("mode") == "Sizing":
        cols = st.columns(4)
        cols[0].metric("Required process duty", _metric_value(result.get("required_duty_W"), 1000, " kW"))
        cols[1].metric("Design duty incl. margin", _metric_value(result.get("design_duty_W"), 1000, " kW"))
        cols[2].metric("Required area", _metric_value(result.get("required_area_m2"), 1, " m²"))
        cols[3].metric("Calculated tube count", str(result.get("tube_count_required", "N/A")))
        cols = st.columns(4)
        cols[0].metric("Installed area", _metric_value(result.get("installed_area_m2"), 1, " m²"))
        cols[1].metric("Predicted capacity", _metric_value(result.get("predicted_capacity_W"), 1000, " kW"))
        cols[2].metric("LMTD", _metric_value((result.get("thermal") or {}).get("LMTD_K"), 1, " K"))
        cols[3].metric("Capacity / design duty", _metric_value(result.get("capacity_ratio"), 1, "×"))
        area_req, area_installed = result.get("required_area_m2"), result.get("installed_area_m2")
        if area_req is not None and area_installed is not None:
            chart = pd.DataFrame({"Area (m²)": [area_req, area_installed]}, index=["Required", "Installed"])
            st.subheader("Preliminary area comparison")
            st.bar_chart(chart)
    else:
        cols = st.columns(4)
        cols[0].metric("Available area", _metric_value(result.get("available_area_m2"), 1, " m²"))
        cols[1].metric("Estimated heat capacity", _metric_value(result.get("capacity_W"), 1000, " kW"))
        cols[2].metric("Target duty", _metric_value(result.get("target_duty_W"), 1000, " kW"))
        cols[3].metric("Capacity / target duty", _metric_value(result.get("capacity_ratio"), 1, "×"))
        cols = st.columns(3)
        cols[0].metric("Target vapor fraction", _metric_value(result.get("target_vapor_fraction"), 1, "", 2))
        cols[1].metric("Estimated vapor fraction", _metric_value(result.get("achieved_vapor_fraction"), 1, "", 2))
        cols[2].metric("LMTD", _metric_value((result.get("thermal") or {}).get("LMTD_K"), 1, " K"))

    st.subheader("Pressure-drop screening estimates")
    p1, p2 = st.columns(2)
    for col, key, title in [(p1, "process_dp", "Process side"), (p2, "hot_dp", "Heating side")]:
        dp = result.get(key) or {}
        with col:
            st.markdown(f"**{title}**")
            if dp.get("delta_p_kPa") is None:
                st.write("Not calculated")
            else:
                st.metric("Estimated ΔP", f"{dp['delta_p_kPa']:.4g} kPa")
                st.write(f"Velocity: {_metric_value(dp.get('velocity_m_s'), 1, ' m/s')}")
                st.write(f"Reynolds number: {_metric_value(dp.get('Reynolds'), 1, '')}")
                st.write(f"Friction factor: {_metric_value(dp.get('friction_factor'), 1, '')}")
                st.caption(str(dp.get("status", "")))

    st.subheader("Thermal calculation basis")
    thermal = result.get("thermal") or {}
    thermal_rows = []
    labels = {
        "sensible_duty_W": "Sensible duty (W)", "latent_duty_W": "Target latent duty (W)",
        "required_duty_W": "Target duty before design margin (W)", "LMTD_K": "Effective LMTD (K)",
        "overall_U_W_m2K": "Assumed overall U (W/m²·K)", "LMTD_correction_factor": "Correction factor F",
    }
    for key, label in labels.items():
        if key in thermal:
            thermal_rows.append({"Parameter": label, "Value": thermal.get(key)})
    if thermal_rows:
        st.dataframe(pd.DataFrame(thermal_rows), use_container_width=True, hide_index=True)

    with st.expander("Calculation trace", expanded=False):
        for step in result.get("calculation_trace", []):
            st.code(step, language="text")
    with st.expander("Inputs used", expanded=False):
        st.markdown("**Process inputs**")
        st.dataframe(pd.DataFrame([{"Parameter": k, "Value": v} for k, v in process_inputs.items()]), use_container_width=True, hide_index=True)
        st.markdown("**Geometry inputs**")
        st.dataframe(pd.DataFrame([{"Parameter": k, "Value": v} for k, v in geometry.items()]), use_container_width=True, hide_index=True)

    warnings = list(result.get("warnings") or [])
    warnings += list(result.get("model_notes") or [])
    checks = result.get("preliminary_checks") or {}
    warnings += list(checks.get("warnings") or [])
    warnings = list(dict.fromkeys(warnings))
    if warnings:
        st.subheader("Warnings and unimplemented physics")
        st.warning("This starter version deliberately uses simplified models. Read the warnings before interpreting any result.")
        for warning in warnings:
            st.write(f"- {warning}")
    else:
        st.success("No warnings were generated by the current preliminary checks. This does not mean the design is validated.")

    report_text = result_to_text(result, process_inputs, geometry)
    st.download_button("Download text report", data=report_text, file_name="evaporator_preliminary_report.txt", mime="text/plain")
    st.download_button("Download result CSV", data=result_to_csv(result), file_name="evaporator_preliminary_results.csv", mime="text/csv")
