"""Common preliminary thermal calculations in SI units internally."""
from __future__ import annotations
import math
from core.unit_conversion import kJ_to_J


def lmtd_for_constant_boiling_temperature(hot_in_C: float, hot_out_C: float, boiling_C: float) -> tuple[float | None, list[str]]:
    """LMTD for a boiling process side treated as constant-temperature.

    This is a simplified arrangement model. It does not account for multiple
    zones, variable saturation temperature, pressure effects, or detailed
    exchanger pass corrections.
    """
    d_t1 = float(hot_in_C) - float(boiling_C)
    d_t2 = float(hot_out_C) - float(boiling_C)
    warnings: list[str] = []
    if d_t1 <= 0 or d_t2 <= 0:
        return None, ["No positive temperature approach at both ends; LMTD cannot be calculated."]
    if math.isclose(d_t1, d_t2, rel_tol=1e-9, abs_tol=1e-9):
        return d_t1, warnings
    ratio = d_t1 / d_t2
    if ratio <= 0 or math.isclose(ratio, 1.0):
        return (d_t1 + d_t2) / 2.0, warnings
    lmtd = (d_t1 - d_t2) / math.log(ratio)
    return lmtd, warnings


def calculate_thermal_basis(p: dict) -> dict:
    """Calculate sensible/latent duties and preliminary effective LMTD."""
    mdot = float(p["mass_flow_kg_s"])
    cp = float(p["cp_kJ_kgK"])
    tin = float(p["inlet_temperature_C"])
    tb = float(p["boiling_temperature_C"])
    hfg = float(p["latent_heat_kJ_kg"])
    x = float(p["target_vapor_fraction"])
    sensible_W = mdot * kJ_to_J(cp) * max(tb - tin, 0.0)
    latent_W = mdot * x * kJ_to_J(hfg)
    required_W = sensible_W + latent_W
    lmtd, warnings = lmtd_for_constant_boiling_temperature(
        p["hot_in_temperature_C"], p["hot_out_temperature_C"], tb
    )
    u = float(p["overall_U_W_m2K"])
    f = float(p["LMTD_correction_factor"])
    if not 0 < f <= 1.5:
        warnings.append("LMTD correction factor is outside the usual preliminary range (0, 1.5]; check this input.")
    return {
        "sensible_duty_W": sensible_W,
        "latent_duty_W": latent_W,
        "required_duty_W": required_W,
        "LMTD_K": lmtd,
        "overall_U_W_m2K": u,
        "LMTD_correction_factor": f,
        "warnings": warnings,
    }


def required_area_m2(duty_W: float, U_W_m2K: float, lmtd_K: float | None, correction_factor: float) -> float | None:
    if lmtd_K is None or lmtd_K <= 0 or U_W_m2K <= 0 or correction_factor <= 0:
        return None
    return float(duty_W) / (float(U_W_m2K) * float(lmtd_K) * float(correction_factor))


def capacity_W(area_m2: float, U_W_m2K: float, lmtd_K: float | None, correction_factor: float) -> float | None:
    if lmtd_K is None or lmtd_K <= 0 or U_W_m2K <= 0 or correction_factor <= 0:
        return None
    return float(area_m2) * float(U_W_m2K) * float(lmtd_K) * float(correction_factor)
