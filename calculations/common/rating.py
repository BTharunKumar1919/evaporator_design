"""Generic preliminary rating workflow used by each exchanger adapter."""
from __future__ import annotations
from calculations.common.thermal import calculate_thermal_basis, capacity_W
from calculations.common.geometry import external_tube_area_m2, tube_side_flow_area_m2
from calculations.common.hydraulics import estimate_exchanger_pressure_drops
from core.validation import validate_process_inputs, validate_geometry


def run_rating(p: dict, g: dict, exchanger_name: str, model_notes: list[str] | None = None, hydraulic_estimator=None) -> dict:
    errors, validation_warnings = validate_process_inputs(p)
    g_errors, g_warnings = validate_geometry(g)
    errors.extend(g_errors)
    validation_warnings.extend(g_warnings)
    if errors:
        return {"mode": "Rating", "exchanger": exchanger_name, "errors": errors,
                "warnings": validation_warnings, "status": "INPUT ERROR"}

    thermal = calculate_thermal_basis(p)
    warnings = validation_warnings + thermal["warnings"] + [
        "The overall heat-transfer coefficient U is an entered assumption, not an exchanger-specific calculated correlation.",
        "Rating area is calculated from tube count, outside diameter, and length; actual bundle layout and inactive area are not accounted for.",
        "Pressure-drop values are single-phase equivalent-channel estimates and are not valid final boiling/two-phase hydraulic calculations.",
        "Pressure-dependent saturation properties, boiling-point elevation, and pressure effects on latent heat are not included.",
    ]
    area = external_tube_area_m2(g["tube_count"], g["tube_od_mm"], g["tube_length_m"])
    capacity = capacity_W(area, thermal["overall_U_W_m2K"], thermal["LMTD_K"], thermal["LMTD_correction_factor"])
    q_sens = thermal["sensible_duty_W"]
    q_latent_available = max(0.0, (capacity or 0.0) - q_sens)
    denominator = float(p["mass_flow_kg_s"]) * float(p["latent_heat_kJ_kg"]) * 1000.0
    achieved_x = min(1.0, q_latent_available / denominator) if denominator > 0 else 0.0
    target_duty = thermal["required_duty_W"]
    capacity_ratio = (capacity / target_duty) if (capacity is not None and target_duty > 0) else None

    hydraulic_result = (hydraulic_estimator or estimate_exchanger_pressure_drops)(p, g, int(g["tube_count"]))
    process_dp = hydraulic_result["process_dp"]
    hot_dp = hydraulic_result["hot_dp"]
    if capacity is None:
        warnings.append("Thermal capacity cannot be calculated because the effective LMTD is invalid.")
    elif capacity < target_duty:
        warnings.append("Estimated heat-transfer capacity is below the target duty.")
    if achieved_x < float(p["target_vapor_fraction"]):
        warnings.append("Predicted vapor fraction is below the target vapor fraction.")
    if process_dp["delta_p_kPa"] is not None and process_dp["delta_p_kPa"] > p["allowable_process_dp_kPa"]:
        warnings.append("Estimated process-side pressure drop exceeds the entered allowable limit.")
    if hot_dp["delta_p_kPa"] is not None and hot_dp["delta_p_kPa"] > p["allowable_hot_dp_kPa"]:
        warnings.append("Estimated heating-side pressure drop exceeds the entered allowable limit.")
    warnings.extend(model_notes or [])
    return {
        "mode": "Rating", "exchanger": exchanger_name, "status": "PRELIMINARY RESULT",
        "errors": [], "warnings": warnings, "thermal": thermal,
        "available_area_m2": area, "capacity_W": capacity,
        "target_duty_W": target_duty, "sensible_duty_W": q_sens,
        "achieved_vapor_fraction": achieved_x,
        "target_vapor_fraction": float(p["target_vapor_fraction"]),
        "capacity_ratio": capacity_ratio,
        "process_dp": process_dp, "hot_dp": hot_dp,
        "model_notes": model_notes or [],
        "calculation_trace": [
            "A_available = N_tubes * pi * tube_OD * tube_length",
            "Q_capacity = U * A_available * LMTD * F",
            "Q_available_for_evaporation = max(Q_capacity - Q_sensible, 0)",
            "x_vapor,estimated = min(1, Q_available_for_evaporation / (m_dot * h_fg))",
        ],
    }
