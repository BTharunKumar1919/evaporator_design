"""Generic preliminary sizing workflow used by each exchanger adapter."""
from __future__ import annotations
from calculations.common.thermal import calculate_thermal_basis, required_area_m2, capacity_W
from calculations.common.geometry import external_tube_area_m2, tube_count_for_area, tube_side_flow_area_m2
from calculations.common.hydraulics import estimate_exchanger_pressure_drops
from core.validation import validate_process_inputs, validate_geometry


def run_sizing(p: dict, g: dict, exchanger_name: str, model_notes: list[str] | None = None, hydraulic_estimator=None) -> dict:
    errors, validation_warnings = validate_process_inputs(p)
    g_errors, g_warnings = validate_geometry(g)
    errors.extend(g_errors)
    validation_warnings.extend(g_warnings)
    if errors:
        return {"mode": "Sizing", "exchanger": exchanger_name, "errors": errors,
                "warnings": validation_warnings, "status": "INPUT ERROR"}

    thermal = calculate_thermal_basis(p)
    warnings = validation_warnings + thermal["warnings"] + [
        "The overall heat-transfer coefficient U is an entered assumption, not an exchanger-specific calculated correlation.",
        "Tube count is calculated from external area only; shell/bundle packing, tube layout, and pass partitioning are not checked.",
        "Pressure-drop values are single-phase equivalent-channel estimates and are not valid final boiling/two-phase hydraulic calculations.",
        "Pressure-dependent saturation properties, boiling-point elevation, and pressure effects on latent heat are not included.",
    ]
    q_design = thermal["required_duty_W"] * float(p["design_margin"])
    area_req = required_area_m2(q_design, thermal["overall_U_W_m2K"], thermal["LMTD_K"], thermal["LMTD_correction_factor"])
    if area_req is None:
        return {"mode": "Sizing", "exchanger": exchanger_name, "errors": [],
                "warnings": warnings + ["Area cannot be calculated because the effective LMTD is invalid."],
                "status": "CALCULATION INCOMPLETE", "thermal": thermal}

    n_tubes = tube_count_for_area(area_req, g["tube_od_mm"], g["tube_length_m"])
    installed_area = external_tube_area_m2(n_tubes, g["tube_od_mm"], g["tube_length_m"])
    capacity = capacity_W(installed_area, thermal["overall_U_W_m2K"], thermal["LMTD_K"], thermal["LMTD_correction_factor"])
    hydraulic_result = (hydraulic_estimator or estimate_exchanger_pressure_drops)(p, g, n_tubes)
    process_dp = hydraulic_result["process_dp"]
    hot_dp = hydraulic_result["hot_dp"]
    if process_dp["delta_p_kPa"] is not None and process_dp["delta_p_kPa"] > p["allowable_process_dp_kPa"]:
        warnings.append("Estimated process-side pressure drop exceeds the entered allowable limit.")
    if hot_dp["delta_p_kPa"] is not None and hot_dp["delta_p_kPa"] > p["allowable_hot_dp_kPa"]:
        warnings.append("Estimated heating-side pressure drop exceeds the entered allowable limit.")
    warnings.extend(model_notes or [])
    return {
        "mode": "Sizing", "exchanger": exchanger_name, "status": "PRELIMINARY RESULT",
        "errors": [], "warnings": warnings, "thermal": thermal,
        "required_duty_W": thermal["required_duty_W"], "design_duty_W": q_design,
        "required_area_m2": area_req, "installed_area_m2": installed_area,
        "tube_count_required": n_tubes, "tube_count_input": int(g["tube_count"]),
        "tube_od_mm": float(g["tube_od_mm"]), "tube_id_mm": float(g["tube_id_mm"]),
        "tube_length_m": float(g["tube_length_m"]), "predicted_capacity_W": capacity,
        "process_dp": process_dp, "hot_dp": hot_dp,
        "capacity_ratio": capacity / q_design if capacity and q_design else None,
        "model_notes": model_notes or [],
        "calculation_trace": [
            "Q_sensible = m_dot * Cp * max(T_boil - T_in, 0)",
            "Q_latent = m_dot * target_vapor_fraction * h_fg",
            "Q_design = (Q_sensible + Q_latent) * design_margin",
            "A_required = Q_design / (U * LMTD * F)",
            "N_tubes = ceiling(A_required / (pi * tube_OD * tube_length))",
            "A_installed = N_tubes * pi * tube_OD * tube_length",
        ],
    }
