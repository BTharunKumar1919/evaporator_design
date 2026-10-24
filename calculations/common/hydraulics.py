"""Preliminary Darcy-Weisbach pressure-drop screening estimate.

This utility is a single-phase, equivalent-channel estimate. It is NOT a valid
final pressure-drop model for boiling/two-phase flow, falling films, pool
boiling, natural circulation, distributors, shell crossflow, or flashing.
"""
from __future__ import annotations
import math
from core.unit_conversion import mm_to_m, Pa_to_kPa


def darcy_pressure_drop_kPa(
    mass_flow_kg_s: float,
    density_kg_m3: float,
    viscosity_Pa_s: float,
    hydraulic_diameter_m: float,
    flow_area_m2: float,
    flow_length_m: float,
    minor_loss_K: float = 2.0,
) -> dict:
    vals = [mass_flow_kg_s, density_kg_m3, viscosity_Pa_s, hydraulic_diameter_m, flow_area_m2, flow_length_m]
    if any(float(v) <= 0 for v in vals):
        return {"delta_p_kPa": None, "velocity_m_s": None, "Reynolds": None, "friction_factor": None,
                "status": "not calculated: one or more inputs are non-positive"}
    mdot, rho, mu, d, area, length = map(float, vals)
    velocity = mdot / (rho * area)
    re = rho * velocity * d / mu
    if re < 1e-12:
        return {"delta_p_kPa": 0.0, "velocity_m_s": velocity, "Reynolds": re,
                "friction_factor": None, "status": "near-zero flow"}
    if re < 2300:
        f = 64.0 / re
        regime = "laminar"
    elif re < 4000:
        f = 0.3164 / (re ** 0.25)
        regime = "transitional; Blasius approximation used"
    else:
        f = 0.3164 / (re ** 0.25)
        regime = "turbulent smooth-pipe Blasius approximation"
    dp_pa = (f * length / d + float(minor_loss_K)) * rho * velocity**2 / 2.0
    return {
        "delta_p_kPa": Pa_to_kPa(dp_pa),
        "velocity_m_s": velocity,
        "Reynolds": re,
        "friction_factor": f,
        "status": regime,
    }


def estimate_exchanger_pressure_drops(p: dict, g: dict, tube_count: int | None = None) -> dict:
    """Estimate equivalent tube-channel and heating-side drops for the GUI starter.

    The process-side proxy assumes the process stream flows inside parallel
    tubes. For types where this is not the actual flow path, the result remains
    illustrative only and the adapter should attach an explicit warning.
    """
    from calculations.common.geometry import tube_side_flow_area_m2
    n = int(tube_count if tube_count is not None else g["tube_count"])
    passes = int(g["tube_passes"])
    process_area = tube_side_flow_area_m2(n, g["tube_id_mm"], passes)
    process = darcy_pressure_drop_kPa(
        p["mass_flow_kg_s"], p["process_density_kg_m3"], p["process_viscosity_Pa_s"],
        mm_to_m(g["tube_id_mm"]), process_area,
        float(g["tube_length_m"]) * passes,
    )
    hot = darcy_pressure_drop_kPa(
        p["hot_mass_flow_kg_s"], p["hot_density_kg_m3"], p["hot_viscosity_Pa_s"],
        p["hot_hydraulic_diameter_m"], p["hot_flow_area_m2"], p["hot_flow_length_m"],
    )
    return {"process_dp": process, "hot_dp": hot}
