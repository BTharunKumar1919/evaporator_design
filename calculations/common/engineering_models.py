"""Source-aligned preliminary thermal design/rating models for five evaporator types.

The methods implemented here follow the uploaded course algorithms where their
inputs and equations are sufficiently specified. Correlation results that the
source documents do not calculate reproducibly are explicit user inputs rather
than silently fabricated values. This is an educational preliminary-design aid,
not a substitute for detailed two-phase, vendor, TEMA or ASME design.
"""
from __future__ import annotations

import math
from typing import Any

from calculations.common.thermal import calculate_thermal_basis
from core.validation import validate_process_inputs, validate_geometry

G = 9.81
AREA_LOWER = 1.10
AREA_UPPER_STANDARD = 1.20
AREA_UPPER_FALLING_FILM = 1.25


def _v(d: dict, key: str, default: float = 0.0) -> float:
    try:
        value = d.get(key, default)
        if value is None or value == "":
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _b(d: dict, key: str, default: bool = False) -> bool:
    return bool(d.get(key, default))


def _vapor_rate(p: dict) -> float:
    """Return explicit vapor generation rate when supplied; otherwise use feed × xe."""
    explicit = _v(p, "vaporization_rate_kg_s", 0.0)
    return explicit if explicit > 0 else _v(p, "mass_flow_kg_s", 1.0) * _v(p, "target_vapor_fraction", 0.2)


def _mm_to_m(x: float) -> float:
    return x / 1000.0


def _effective_dt(p: dict, thermal: dict) -> tuple[float | None, list[str]]:
    raw = thermal.get("LMTD_K")
    f = _v(p, "LMTD_correction_factor", 1.0)
    if raw is None or raw <= 0 or f <= 0:
        return None, ["Effective temperature difference is invalid; no valid positive LMTD × F was obtained."]
    return raw * f, []


def _pitch_and_bundle(g: dict, n: int, auto_bundle: bool) -> tuple[float, float, list[str]]:
    do = _mm_to_m(_v(g, "tube_od_mm", 19.0))
    pitch_ratio = _v(g, "tube_pitch_ratio", 1.25)
    pitch = _v(g, "tube_pitch_m", 0.0) or pitch_ratio * do
    warnings: list[str] = []
    if auto_bundle and n > 0 and pitch > 0:
        # Same simple bundle estimate used in the horizontal-thermosyphon example.
        db = 1.1 * math.sqrt(n) * pitch
        warnings.append("Bundle diameter is estimated with Db ≈ 1.1·sqrt(Nt)·Pt; it is not a TEMA tube-layout calculation.")
    else:
        db = _v(g, "bundle_diameter_m", 0.45)
    return pitch, max(db, 1e-6), warnings


def _mostinski_baseline_note() -> str:
    return ("The supplied Mostinski equation/substitution is not reproducible from the PDF as written (units/arithmetic are inconsistent). "
            "The baseline nucleate-boiling HTC is therefore taken from the explicit input, not claimed as a computed Mostinski result.")


def _pool_boiling_htc(p: dict, g: dict, n: int, area: float, duty: float, auto_bundle: bool) -> dict:
    do = _mm_to_m(_v(g, "tube_od_mm", 19.0))
    length = _v(g, "tube_length_m", 3.0)
    pt, db, bundle_notes = _pitch_and_bundle(g, n, auto_bundle)
    layout = str(g.get("tube_layout", "Square"))
    ci = 0.866 if "triang" in layout.lower() or "stagger" in layout.lower() else 1.0
    pitch_ratio = max(pt / max(do, 1e-12), 1.0)
    bracket = (0.785 * db) / (ci * (pitch_ratio ** 2) * max(do, 1e-12)) - 1.0
    fb = 1.0 + 0.1 * max(bracket, 0.0) ** 0.75
    q_flux = max(duty / max(area, 1e-12), 1e-9)
    # The source does not define the heat-flux unit used in Fs. Use kW/m2 and expose this assumption.
    q_kw_m2 = q_flux / 1000.0
    br = max(_v(p, "boiling_range_C", 0.0), 0.0)
    fs = 1.0 + 0.023 * (q_kw_m2 ** 0.15) * (br ** 0.75 if br > 0 else 0.0)
    hnb = max(_v(p, "pool_boiling_htc_W_m2K", 5000.0), 1.0)
    hnc = max(_v(p, "natural_convection_htc_W_m2K", 250.0), 0.0)
    hb = hnb * fb * fs + hnc
    warnings = bundle_notes + [_mostinski_baseline_note()]
    if br > 0:
        warnings.append("Mixture factor Fs uses q in kW/m² as a documented coding convention; the source PDF does not clearly state the units in its Fs expression.")
    return {
        "process_htc_W_m2K": hb,
        "pool_boiling_baseline_htc_W_m2K": hnb,
        "bundle_factor_Fb": fb,
        "mixture_factor_Fs": fs,
        "natural_convection_htc_W_m2K": hnc,
        "heat_flux_W_m2": q_flux,
        "bundle_diameter_m_used": db,
        "tube_pitch_m_used": pt,
        "warnings": warnings,
    }


def _falling_film_htc(p: dict, g: dict, n: int) -> dict:
    di = _mm_to_m(_v(g, "tube_id_mm", 16.0))
    mu = _v(p, "process_viscosity_Pa_s", 0.001)
    rho = _v(p, "process_density_kg_m3", 1000.0)
    k = _v(p, "process_thermal_conductivity_W_mK", 0.62)
    cp = _v(p, "cp_kJ_kgK", 4.18) * 1000.0
    mdot = _v(p, "mass_flow_kg_s", 1.0)
    x = min(max(_v(p, "target_vapor_fraction", 0.2), 0.0), 0.999999)
    mvap = _vapor_rate(p)
    mliq_out = max(mdot - mvap, 0.0)
    perimeter = max(n * math.pi * di, 1e-12)
    gamma_in = mdot / perimeter
    gamma_out = mliq_out / perimeter
    gamma_mean = 0.5 * (gamma_in + gamma_out)
    re_f = 4.0 * gamma_mean / max(mu, 1e-20)
    re_in = 4.0 * gamma_in / max(mu, 1e-20)
    re_out = 4.0 * gamma_out / max(mu, 1e-20)
    pr = mu * cp / max(k, 1e-20)
    re_crit = 5800.0 * max(pr, 1e-12) ** -1.06
    base = ((k ** 3) * (rho ** 2) * G / max(mu ** 2, 1e-30)) ** (1.0 / 3.0)
    if re_f <= 30.0:
        regime = "laminar"
        h_star = 1.1006 * max(re_f, 1e-12) ** (-1.0 / 3.0)
    elif re_f <= re_crit:
        regime = "wavy-laminar"
        h_star = 0.821 * max(re_f, 1e-12) ** (-0.22)
    else:
        regime = "turbulent"
        h_star = 0.0038 * max(re_f, 1e-12) ** 0.4 * max(pr, 1e-12) ** 0.65
    hi = base * h_star
    delta = (3.0 * mu * max(gamma_mean, 1e-20) / max(rho ** 2 * G, 1e-20)) ** (1.0 / 3.0)
    hfg = _v(p, "latent_heat_kJ_kg", 2300.0) * 1000.0
    f_kl = gamma_in * hfg
    q_latent = mvap * hfg
    q_l_perimeter = q_latent / perimeter
    palen_ratio = f_kl / max(q_l_perimeter, 1e-20)
    gamma_min = _v(p, "minimum_film_wetting_rate_kg_m_s", 0.05)
    warnings = []
    if re_f <= 30:
        warnings.append("Falling-film HTC is using the laminar Nusselt-film expression.")
    if gamma_min <= 0:
        warnings.append("Minimum wetting-rate input is non-positive; the minimum wetting check cannot be interpreted.")
    return {
        "process_htc_W_m2K": hi,
        "film_regime": regime,
        "film_Reynolds_mean": re_f,
        "film_Reynolds_inlet": re_in,
        "film_Reynolds_outlet": re_out,
        "film_critical_Reynolds": re_crit,
        "film_Prandtl": pr,
        "film_thickness_estimate_m": delta,
        "wetting_rate_in_kg_m_s": gamma_in,
        "wetting_rate_out_kg_m_s": gamma_out,
        "wetting_rate_mean_kg_m_s": gamma_mean,
        "minimum_wetting_rate_kg_m_s": gamma_min,
        "Palen_Fkl_W_m": f_kl,
        "Palen_qL_W_m": q_l_perimeter,
        "Palen_ratio_Fkl_over_qL": palen_ratio,
        "Palen_dryout_pass": f_kl > 1.5 * q_l_perimeter,
        "minimum_wetting_pass": gamma_out >= gamma_min,
        "warnings": warnings,
    }


def _forced_circulation_htc(p: dict, g: dict, n: int, mode: str) -> dict:
    di = _mm_to_m(_v(g, "tube_id_mm", 16.0))
    passes = max(int(_v(g, "tube_passes", 1)), 1)
    nt = max(int(n), 1)
    n_tubes_per_pass = nt / passes
    flow_area = max(n_tubes_per_pass * math.pi * di ** 2 / 4.0, 1e-12)
    target_u = _v(p, "forced_circulation_velocity_m_s", 3.0)
    if mode == "Sizing":
        velocity = target_u
        pump_rate = velocity * flow_area
    else:
        pump_rate = _v(p, "pump_flow_rate_m3_s", 0.05)
        velocity = pump_rate / flow_area if pump_rate > 0 else target_u
    rho = _v(p, "process_density_kg_m3", 1000.0)
    mu = _v(p, "process_viscosity_Pa_s", 0.001)
    k = _v(p, "process_thermal_conductivity_W_mK", 0.62)
    cp = _v(p, "cp_kJ_kgK", 4.18) * 1000.0
    pr = mu * cp / max(k, 1e-20)
    re = rho * velocity * di / max(mu, 1e-20)
    nu = 0.023 * max(re, 1e-12) ** 0.8 * max(pr, 1e-12) ** 0.4
    hi = nu * k / max(di, 1e-12)
    warnings = []
    if re < 10000:
        warnings.append("Dittus–Boelter is normally used for fully turbulent tube flow; the calculated Reynolds number is below 10,000, so HTC is extrapolative.")
    if not 2.0 <= velocity <= 5.0:
        warnings.append("Forced-circulation velocity is outside the source algorithm's 2–5 m/s suppression-velocity target.")
    # Smooth/turbulent Darcy screening using the example's f = 0.015; not two-phase pressure drop.
    f = 0.015
    length = _v(g, "tube_length_m", 3.0) * passes
    dp_pa = f * length / max(di, 1e-12) * rho * velocity ** 2 / 2.0
    return {
        "process_htc_W_m2K": hi,
        "tube_velocity_m_s": velocity,
        "pump_flow_rate_m3_s": pump_rate,
        "tube_flow_area_m2": flow_area,
        "tube_Reynolds": re,
        "tube_Prandtl": pr,
        "tube_Nusselt": nu,
        "darcy_friction_factor_assumed": f,
        "tube_friction_dp_kPa_estimate": dp_pa / 1000.0,
        "warnings": warnings,
    }


def _u_overall(p: dict, g: dict, exchanger: str, h_process: float, h_hot: float) -> dict:
    do = _mm_to_m(_v(g, "tube_od_mm", 19.0))
    di = _mm_to_m(_v(g, "tube_id_mm", 16.0))
    kw = _v(p, "tube_wall_conductivity_W_mK", 16.0)
    if do <= di or di <= 0 or kw <= 0 or h_process <= 0 or h_hot <= 0:
        return {"Uo_W_m2K": _v(p, "overall_U_W_m2K", 1200.0), "resistances_m2K_W": {},
                "warnings": ["Invalid tube dimensions or heat-transfer coefficients; using the entered overall-U fallback."]}
    rwall = do * math.log(do / di) / (2.0 * kw)
    rf_process = _v(p, "cold_fouling_factor_m2K_W", 0.0002)
    rf_hot = _v(p, "hot_fouling_factor_m2K_W", 0.0001)
    process_inside = exchanger in {"Forced Circulation Evaporator", "Vertical Thermosyphon Reboiler", "Falling Film Evaporator"}
    if process_inside:
        r_inside_conv = do / (di * h_process)
        r_inside_foul = rf_process * do / di
        r_outside_foul = rf_hot
        r_outside_conv = 1.0 / h_hot
    else:
        r_inside_conv = do / (di * h_hot)
        r_inside_foul = rf_hot * do / di
        r_outside_foul = rf_process
        r_outside_conv = 1.0 / h_process
    terms = {
        "tube_side_convection": r_inside_conv,
        "tube_side_fouling": r_inside_foul,
        "tube_wall_conduction": rwall,
        "shell_side_fouling": r_outside_foul,
        "shell_side_convection": r_outside_conv,
    }
    total = sum(terms.values())
    return {"Uo_W_m2K": 1.0 / total, "resistances_m2K_W": terms, "warnings": []}


def _chf_check(p: dict, g: dict, n: int, area: float, duty: float, exchanger: str, auto_bundle: bool) -> dict:
    rho_l = _v(p, "process_density_kg_m3", 1000.0)
    rho_v = _v(p, "process_vapor_density_kg_m3", 1.2)
    sigma = _v(p, "process_surface_tension_N_m", 0.05)
    hfg = _v(p, "latent_heat_kJ_kg", 2300.0) * 1000.0
    do = _mm_to_m(_v(g, "tube_od_mm", 19.0))
    length = _v(g, "tube_length_m", 3.0)
    x = _v(p, "target_vapor_fraction", 0.2)
    _, db, bundle_notes = _pitch_and_bundle(g, n, auto_bundle)
    valid = rho_l > rho_v and sigma > 0 and hfg > 0 and area > 0
    if not valid:
        return {"chf_check_status": "NOT CALCULATED", "warnings": bundle_notes + ["CHF correlation requires positive latent heat/surface tension and liquid density greater than vapor density."]}
    q_tube = 0.131 * hfg * math.sqrt(rho_v) * (sigma * G * (rho_l - rho_v)) ** 0.25
    if exchanger == "Kettle Reboiler":
        pt, _, _ = _pitch_and_bundle(g, n, auto_bundle)
        phi = 3.1 * pt / (math.pi * max(db, 1e-12))
    else:
        phi = 3.1 * (math.pi * db * length / max(area, 1e-12))
    q_bundle = phi * q_tube
    q_actual = duty / max(area, 1e-12)
    pass_flux = q_actual <= 0.7 * q_bundle
    quality_cap_applies = exchanger in {"Vertical Thermosyphon Reboiler"}
    pass_quality = (x <= 0.25) if quality_cap_applies else None
    warnings = bundle_notes
    if not pass_flux:
        warnings.append("Operating heat flux exceeds 70% of the calculated bundle CHF; the source algorithm flags a dry-out / film-boiling risk.")
    if quality_cap_applies and not pass_quality:
        warnings.append("Exit vapor mass fraction exceeds the vertical-thermosyphon 25% quality cap stated in the source algorithm.")
    return {
        "CHF_single_tube_W_m2": q_tube,
        "CHF_bundle_factor_phi_b": phi,
        "CHF_bundle_W_m2": q_bundle,
        "operating_heat_flux_W_m2": q_actual,
        "CHF_allowable_70pct_W_m2": 0.7 * q_bundle,
        "CHF_flux_pass": pass_flux,
        "exit_quality_fraction": x,
        "exit_quality_cap_applies": quality_cap_applies,
        "exit_quality_pass": pass_quality,
        "chf_check_status": "PASS" if pass_flux and pass_quality is not False else "FAIL",
        "warnings": warnings,
    }


def _natural_circulation(p: dict, g: dict, x: float, exchanger: str) -> dict:
    rho_l = _v(p, "process_density_kg_m3", 1000.0)
    rho_v = _v(p, "process_vapor_density_kg_m3", 1.2)
    h_static = _v(g, "static_elevation_m", _v(p, "static_elevation_m", 1.8))
    length = _v(g, "tube_length_m", 3.0)
    x_safe = min(max(x, 1e-8), 0.999999)
    r = (1.0 - x_safe) / x_safe
    alpha = 1.0 / (1.0 + ((1.0 - x_safe) / x_safe) * (rho_v / max(rho_l, 1e-20)) ** (2.0 / 3.0))
    rho_tp = rho_l * (1.0 - alpha) + rho_v * alpha
    dp_drive = rho_l * G * h_static
    # A horizontal thermosyphon tube run does not create a rho_tp*g*L head
    # over its full tube length. Vertical thermosyphon uses the tube length as
    # a first-pass vertical two-phase rise; detailed elevation profile is still
    # required for an engineering loop balance.
    vertical_rise = length if exchanger == "Vertical Thermosyphon Reboiler" else 0.0
    dp_two_phase_gravity = rho_tp * G * vertical_rise
    dp_extra = p.get("estimated_natural_loop_dp_kPa")
    try:
        dp_extra_kpa = float(dp_extra) if dp_extra not in (None, "") else None
    except (TypeError, ValueError):
        dp_extra_kpa = None
    if dp_extra_kpa is None:
        status = "UNKNOWN: friction/acceleration loss was not supplied; full loop balance cannot be confirmed."
        balance = None
        warnings = ["Natural-circulation loop balance is not certified because friction and acceleration pressure drops are not derived from the available inputs."]
    elif exchanger == "Horizontal Thermosyphon Reboiler":
        # For horizontal orientation, the provided selection algorithm screens
        # the estimated loop-loss value against the available static head and
        # allowable pressure drop; it does not supply a full elevation profile.
        allowable_dp = _v(p, "allowable_process_dp_kPa", 100.0)
        balance = dp_extra_kpa < dp_drive / 1000.0 and dp_extra_kpa <= allowable_dp
        status = "PASS source static-head/allowable-ΔP screen" if balance else "FAIL source static-head/allowable-ΔP screen"
        warnings = ["Horizontal thermosyphon riser/downcomer elevations and two-phase friction/acceleration losses are not solved; this is the course selection gate, not a closed-loop hydraulic balance."]
        if not balance:
            warnings.append("Estimated natural-loop loss is not below both the available static-head screen and the entered allowable process-side pressure drop.")
    else:
        dp_total = dp_two_phase_gravity + dp_extra_kpa * 1000.0
        err_pct = abs(dp_drive - dp_total) / max(dp_drive, 1e-12) * 100.0
        balance = err_pct <= 5.0
        status = "PASS (within 5%)" if balance else "FAIL (outside 5%)"
        warnings = [] if balance else ["Estimated natural-loop pressure balance differs from the source algorithm's driving head by more than 5%."]
    if (exchanger == "Vertical Thermosyphon Reboiler" and abs(x_safe - 0.10) <= 0.02
            and abs(rho_l - 958.0) <= 15.0 and abs(rho_v - 0.598) <= 0.15):
        warnings.append("Source-example consistency warning: the vertical-thermosyphon PDF reports Zivi alpha ≈ 0.82 at 10% quality, but its printed 2/3-power Zivi expression and listed densities imply a substantially different alpha (about 0.94). The code follows the printed expression; verify the worked example's exponent/properties.")
    return {
        "recirculation_ratio_R": r,
        "Zivi_void_fraction_alpha": alpha,
        "two_phase_mixture_density_kg_m3": rho_tp,
        "static_driving_pressure_kPa": dp_drive / 1000.0,
        "two_phase_gravity_drop_kPa": dp_two_phase_gravity / 1000.0,
        "user_estimated_friction_acceleration_drop_kPa": dp_extra_kpa,
        "natural_loop_balance_status": status,
        "natural_loop_balance_pass": balance,
        "warnings": warnings,
    }


def _disengagement(p: dict, g: dict, mode: str, n: int, auto_bundle: bool, exchanger: str) -> dict:
    _, db, bundle_notes = _pitch_and_bundle(g, n, auto_bundle)
    ds = _v(g, "shell_diameter_m", 0.5)
    hw = _v(g, "weir_height_m", _v(g, "liquid_level_m", 0.3))
    ds_required = 1.4 * db + 0.1
    diameter_gate_applies = exchanger in {"Horizontal Thermosyphon Reboiler", "Kettle Reboiler"}
    ds_pass = (ds >= ds_required if mode == "Rating" or not auto_bundle else True) if diameter_gate_applies else None
    rho_l = _v(p, "process_density_kg_m3", 1000.0)
    rho_v = _v(p, "process_vapor_density_kg_m3", 1.2)
    mvap = _vapor_rate(p)
    ksb = _v(p, "souders_brown_K_m_s", 0.1)
    free_area = math.pi / 4.0 * max(ds ** 2 - db ** 2, 1e-8)
    uv = mvap / max(rho_v * free_area, 1e-12)
    uv_max = 0.75 * ksb * math.sqrt(max(rho_l - rho_v, 0.0) / max(rho_v, 1e-12))
    velocity_pass = uv <= uv_max
    warnings = bundle_notes
    if ds_pass is False:
        warnings.append("Shell diameter fails the source screen Ds ≥ 1.4·Db + 0.10 m; vapor disengagement / entrainment risk is flagged.")
    if not velocity_pass:
        warnings.append("Estimated vapor velocity exceeds 75% of the Souders–Brown velocity limit; entrainment risk is flagged. Verify K and the actual disengagement area.")
    if free_area <= 1e-7:
        warnings.append("Shell free area is non-positive or near-zero; vapor velocity estimate is not reliable.")
    return {
        "bundle_diameter_m_used": db,
        "shell_diameter_m_input": ds,
        "shell_diameter_required_m": ds_required,
        "shell_diameter_check_applies": diameter_gate_applies,
        "shell_diameter_check_pass": ds_pass,
        "estimated_disengagement_height_m": ds - db - hw,
        "vapor_free_area_m2_estimate": free_area,
        "vapor_velocity_m_s_estimate": uv,
        "Souders_Brown_velocity_limit_m_s_estimate": uv_max,
        "vapor_disengagement_velocity_pass": velocity_pass,
        "warnings": warnings,
    }


def _falling_film_distributor(p: dict, g: dict, n: int) -> dict:
    rho = _v(p, "process_density_kg_m3", 1000.0)
    mdot = _v(p, "mass_flow_kg_s", 1.0)
    holes = max(int(_v(g, "distributor_hole_count", max(2 * n, 2))), 1)
    dh = _mm_to_m(_v(g, "distributor_hole_diameter_mm", 3.8))
    cd = _v(g, "distributor_discharge_coefficient", 0.62)
    denominator = rho * holes * cd * (math.pi * dh ** 2 / 4.0)
    head = (mdot / denominator) ** 2 / (2.0 * G) if denominator > 0 else None
    passed = head is not None and 0.025 <= head <= 0.2
    warnings = []
    if head is not None and not passed:
        warnings.append("Calculated distributor head is outside the source's 25–200 mm liquid-head range; review hole count/diameter and maldistribution risk.")
    if holes < 2 * n or holes > 4 * n:
        warnings.append("The source suggests roughly 2–4 distributor holes per tube; the current hole count is outside that screen.")
    return {
        "distributor_hole_count": holes,
        "distributor_hole_diameter_m": dh,
        "distributor_discharge_coefficient": cd,
        "required_distributor_liquid_head_m": head,
        "distributor_head_check_pass": passed,
        "warnings": warnings,
    }


def _mechanical_checks(p: dict, g: dict) -> dict:
    p_design_mpa = _v(p, "design_pressure_MPa", 0.0)
    allowable_stress_mpa = _v(p, "allowable_stress_MPa", 138.0)
    joint_eff = _v(p, "joint_efficiency", 1.0)
    ca_mm = _v(p, "corrosion_allowance_mm", 0.0)
    do_mm = _v(g, "tube_od_mm", 19.0)
    t_existing_mm = do_mm - _v(g, "tube_id_mm", 16.0)
    if p_design_mpa <= 0:
        return {
            "required_wall_thickness_mm": None,
            "estimated_existing_wall_thickness_mm": t_existing_mm,
            "wall_thickness_check_status": "NOT CHECKED: enter design pressure and verified allowable stress/joint efficiency.",
            "warnings": ["ASME UG-27 / TEMA mechanical compliance is not established from operating pressure alone. Enter design pressure, material allowable stress, joint efficiency and corrosion allowance for a preliminary thickness screen."],
        }
    den = 2.0 * allowable_stress_mpa * joint_eff + 0.8 * p_design_mpa
    if den <= 0 or allowable_stress_mpa <= 0 or not 0 < joint_eff <= 1:
        return {"required_wall_thickness_mm": None, "estimated_existing_wall_thickness_mm": t_existing_mm,
                "wall_thickness_check_status": "INVALID INPUTS", "warnings": ["Invalid stress/joint-efficiency values for the preliminary wall-thickness equation."]}
    t_req = p_design_mpa * do_mm / den + ca_mm
    passed = t_existing_mm >= t_req
    return {
        "required_wall_thickness_mm": t_req,
        "estimated_existing_wall_thickness_mm": t_existing_mm,
        "wall_thickness_check_status": "PASS preliminary equation" if passed else "FAIL preliminary equation",
        "warnings": [] if passed else ["Calculated wall thickness is below the preliminary pressure-thickness equation; detailed code design is required."],
    }


def _specific_results(mode: str, p: dict, g: dict, exchanger: str, n: int, area: float, duty: float, auto_bundle: bool) -> dict:
    warnings: list[str] = []
    dt = _v(p, "_effective_dt_K", 0.0)
    h_hot = max(_v(p, "heating_htc_W_m2K", 6000.0), 1.0)
    metrics: dict[str, Any] = {}
    if exchanger == "Forced Circulation Evaporator":
        details = _forced_circulation_htc(p, g, n, mode)
        h_process = details.pop("process_htc_W_m2K")
        metrics.update(details)
        warnings.extend(details.get("warnings", []))
    elif exchanger in {"Horizontal Thermosyphon Reboiler", "Kettle Reboiler"}:
        details = _pool_boiling_htc(p, g, n, area, duty, auto_bundle)
        h_process = details.pop("process_htc_W_m2K")
        metrics.update(details)
        warnings.extend(details.get("warnings", []))
    elif exchanger == "Falling Film Evaporator":
        details = _falling_film_htc(p, g, n)
        h_process = details.pop("process_htc_W_m2K")
        metrics.update(details)
        warnings.extend(details.get("warnings", []))
    else:  # Vertical thermosyphon uses Chen's correlation result as a separately-entered/seeded value.
        h_process = max(_v(p, "process_boiling_htc_W_m2K", 3900.0), 1.0)
        metrics["process_boiling_htc_W_m2K_used"] = h_process
        warnings.append("Vertical-thermosyphon Chen HTC is supplied as an explicit effective coefficient; the source example does not provide enough property/correlation detail to reproduce every Chen term reliably.")
    u_calc = _u_overall(p, g, exchanger, h_process, h_hot)
    warnings.extend(u_calc.get("warnings", []))
    metrics["process_side_htc_W_m2K"] = h_process
    metrics["heating_side_htc_W_m2K_used"] = h_hot
    metrics["overall_U_W_m2K_calculated"] = u_calc["Uo_W_m2K"]
    metrics["overall_U_resistance_terms_m2K_W"] = u_calc["resistances_m2K_W"]
    if exchanger in {"Vertical Thermosyphon Reboiler", "Horizontal Thermosyphon Reboiler"}:
        natural = _natural_circulation(p, g, _v(p, "target_vapor_fraction", 0.2), exchanger)
        metrics.update(natural)
        warnings.extend(natural.get("warnings", []))
    if exchanger in {"Vertical Thermosyphon Reboiler", "Horizontal Thermosyphon Reboiler", "Kettle Reboiler"}:
        chf = _chf_check(p, g, n, area, duty, exchanger, auto_bundle)
        metrics.update(chf)
        warnings.extend(chf.get("warnings", []))
        disengagement = _disengagement(p, g, mode, n, auto_bundle, exchanger)
        metrics.update(disengagement)
        warnings.extend(disengagement.get("warnings", []))
    if exchanger == "Falling Film Evaporator":
        ff = _falling_film_distributor(p, g, n)
        metrics.update(ff)
        warnings.extend(ff.get("warnings", []))
        # The falling-film vapor core/flooding screen is approximate because no detailed core geometry is supplied.
        rho_v = _v(p, "process_vapor_density_kg_m3", 1.2)
        mvap = _vapor_rate(p)
        di = _mm_to_m(_v(g, "tube_id_mm", 16.0))
        core_area = max(n * math.pi * di ** 2 / 4.0, 1e-12)
        ug = mvap / max(rho_v * core_area, 1e-12)
        ul = max(_v(p, "mass_flow_kg_s", 1.0) - mvap, 0.0) / max(_v(p, "process_density_kg_m3", 1000.0) * core_area, 1e-12)
        rho_l = _v(p, "process_density_kg_m3", 1000.0)
        denom = max(G * di * max(rho_l - rho_v, 1e-12), 1e-12)
        wallis_g = ug * math.sqrt(max(rho_v, 1e-12) / denom)
        wallis_l = ul * math.sqrt(max(rho_l, 1e-12) / denom)
        wallis_sum = math.sqrt(max(wallis_g, 0.0)) + math.sqrt(max(wallis_l, 0.0))
        wallis_limit = _v(p, "wallis_flooding_limit", 0.725)
        metrics.update({"falling_film_vapor_core_velocity_m_s_estimate": ug,
                        "falling_film_liquid_velocity_m_s_proxy": ul,
                        "Wallis_flooding_sum_estimate": wallis_sum,
                        "Wallis_flooding_limit_input": wallis_limit,
                        "Wallis_flooding_check_pass": wallis_sum <= wallis_limit})
        if wallis_sum > wallis_limit:
            warnings.append("Wallis flooding screen exceeds the entered limit; verify using the source's complete two-phase geometry and properties.")
    mechanical = _mechanical_checks(p, g)
    metrics.update(mechanical)
    warnings.extend(mechanical.get("warnings", []))
    return {"metrics": metrics, "U_W_m2K": u_calc["Uo_W_m2K"], "warnings": list(dict.fromkeys(warnings))}


def _recommend_geometry(g: dict, n: int, exchanger: str, auto_bundle: bool) -> dict:
    out = dict(g)
    out["tube_count"] = int(n)
    pt, db, _ = _pitch_and_bundle(g, n, auto_bundle)
    out["tube_pitch_m"] = pt
    if auto_bundle:
        out["bundle_diameter_m"] = db
    if auto_bundle and exchanger in {"Horizontal Thermosyphon Reboiler", "Kettle Reboiler"}:
        out["shell_diameter_m"] = max(_v(g, "shell_diameter_m", 0.5), 1.4 * db + 0.1)
    return out


def _common_validation(p: dict, g: dict) -> tuple[list[str], list[str]]:
    errors, warnings = validate_process_inputs(p)
    g_errors, g_warnings = validate_geometry(g)
    errors.extend(g_errors)
    warnings.extend(g_warnings)
    do = _v(g, "tube_od_mm", 19.0)
    di = _v(g, "tube_id_mm", 16.0)
    if di >= do:
        errors.append("Tube inside diameter must be smaller than outside diameter.")
    if _v(p, "process_thermal_conductivity_W_mK", 0.62) <= 0:
        errors.append("Process thermal conductivity must be positive.")
    if _v(p, "process_vapor_density_kg_m3", 1.2) <= 0:
        errors.append("Process vapor density must be positive for the supplied two-phase checks.")
    if _v(p, "heating_htc_W_m2K", 6000.0) <= 0:
        errors.append("Heating-side HTC must be positive.")
    return errors, warnings


def run_equipment_calculation(mode: str, p: dict, g: dict, exchanger: str) -> dict:
    """Execute a source-aligned equipment-specific preliminary sizing/rating run."""
    if mode not in {"Sizing", "Rating"}:
        raise ValueError("Mode must be 'Sizing' or 'Rating'.")
    errors, input_warnings = _common_validation(p, g)
    if errors:
        return {"mode": mode, "exchanger": exchanger, "errors": errors, "warnings": input_warnings, "status": "INPUT ERROR"}

    thermal = calculate_thermal_basis(p)
    # The supplied forced-circulation worked examples use a mixed sensible/latent
    # temperature profile: hot-in minus feed-in at one end, hot-out minus boiling
    # temperature at the other. The other four source examples use a constant-
    # boiling-temperature approach. Keep these bases distinct instead of forcing
    # all equipment through one LMTD expression.
    if exchanger == "Forced Circulation Evaporator":
        dt1 = _v(p, "hot_in_temperature_C", 0.0) - _v(p, "inlet_temperature_C", 0.0)
        dt2 = _v(p, "hot_out_temperature_C", 0.0) - _v(p, "boiling_temperature_C", 0.0)
        if dt1 > 0 and dt2 > 0:
            if math.isclose(dt1, dt2, rel_tol=1e-9, abs_tol=1e-9):
                lmtd_mixed = dt1
            else:
                lmtd_mixed = (dt1 - dt2) / math.log(dt1 / dt2)
            thermal["LMTD_K"] = lmtd_mixed
            thermal["LMTD_method"] = "Forced-circulation mixed sensible/latent source method: LMTD(hot inlet − process feed, hot outlet − process boiling temperature)"
            thermal["LMTD_terminal_differences_K"] = {"hot_in_minus_feed_in": dt1, "hot_out_minus_boiling": dt2}
        else:
            thermal["LMTD_K"] = None
            thermal["warnings"] = list(thermal.get("warnings", [])) + [
                "Forced-circulation mixed sensible/latent LMTD requires hot-in > feed-in and hot-out > process boiling temperature."
            ]
    else:
        thermal["LMTD_method"] = "Constant-boiling process-side LMTD used by the supplied source examples for this equipment type."
    dt, dt_warnings = _effective_dt(p, thermal)
    warnings = list(input_warnings) + list(thermal.get("warnings", [])) + dt_warnings
    if dt is None or dt <= 0:
        return {"mode": mode, "exchanger": exchanger, "errors": [], "warnings": warnings,
                "status": "CALCULATION INCOMPLETE", "thermal": thermal}

    q = _v(thermal, "required_duty_W")
    margin = max(_v(p, "design_margin", 1.0), 1.0)
    q_for_design = q * margin
    per_tube_area = math.pi * _mm_to_m(_v(g, "tube_od_mm", 19.0)) * _v(g, "tube_length_m", 3.0)
    if per_tube_area <= 0:
        return {"mode": mode, "exchanger": exchanger, "errors": ["Tube area per tube is not positive."], "warnings": warnings, "status": "INPUT ERROR"}
    upper = AREA_UPPER_FALLING_FILM if exchanger == "Falling Film Evaporator" else AREA_UPPER_STANDARD
    seed_u = {"Forced Circulation Evaporator": 1200.0, "Horizontal Thermosyphon Reboiler": 1200.0,
              "Vertical Thermosyphon Reboiler": 2000.0, "Kettle Reboiler": 1700.0,
              "Falling Film Evaporator": 2000.0}.get(exchanger, 1200.0)
    auto_bundle = (mode == "Sizing") and _b(g, "auto_bundle_geometry", True)
    trace: list[str] = []

    if mode == "Sizing":
        n = max(1, int(math.ceil(q_for_design / max(seed_u * dt * per_tube_area, 1e-12))))
        target_ratio = (AREA_LOWER + upper) / 2.0
        last = None
        for iteration in range(1, 41):
            recommended_g = _recommend_geometry(g, n, exchanger, auto_bundle)
            area = n * per_tube_area
            local_p = dict(p)
            local_p["_effective_dt_K"] = dt
            spec = _specific_results(mode, local_p, recommended_g, exchanger, n, area, q_for_design, auto_bundle)
            u = spec["U_W_m2K"]
            req_area = q_for_design / max(u * dt, 1e-12)
            ratio = area / req_area
            trace.append(f"Sizing iteration {iteration}: Nt={n}, Acalc={area:.4f} m², Uo={u:.3f} W/m²K, Areq={req_area:.4f} m², Acalc/Areq={ratio:.4f}.")
            last = (recommended_g, area, spec, req_area, ratio, u)
            if AREA_LOWER <= ratio <= upper:
                break
            n_new = max(1, int(math.ceil(req_area * target_ratio / per_tube_area)))
            if n_new == n:
                n_new = n + 1 if ratio < AREA_LOWER else max(1, n - 1)
            n = n_new
        assert last is not None
        recommended_g, installed_area, spec, area_req, area_ratio, u = last
        if not (AREA_LOWER <= area_ratio <= upper):
            warnings.append(f"Sizing iteration did not converge to the prescribed area band [{AREA_LOWER:.2f}, {upper:.2f}] within 40 iterations; review HTC and geometry assumptions.")
        thermal["overall_U_W_m2K"] = u
        thermal["LMTD_K"] = dt
        thermal["raw_LMTD_K"] = dt / max(_v(p, "LMTD_correction_factor", 1.0), 1e-12)
        thermal["effective_temperature_difference_K"] = dt
        capacity = u * installed_area * dt
        q_rating = capacity
        x_achieved = min(max((capacity - thermal["sensible_duty_W"]) / max(_v(p, "mass_flow_kg_s", 1.0) * _v(p, "latent_heat_kJ_kg", 2300.0) * 1000.0, 1e-12), 0.0), 1.0)
        hydraulics = _hydraulic_output(mode, p, recommended_g, exchanger, n, spec["metrics"])
        warnings.extend(spec["warnings"])
        warnings.extend(hydraulics["warnings"])
        checks = _summarize_checks(exchanger, spec["metrics"], area_ratio, lower=AREA_LOWER, upper=upper, mode=mode)
        warnings.extend(checks["warnings"])
        warnings = list(dict.fromkeys(warnings))
        trace.extend([
            f"Q_sensible = m_dot·Cp·max(Tb−Tin,0) = {thermal['sensible_duty_W']:.3f} W.",
            f"Q_latent = m_dot·xe·h_fg = {thermal['latent_duty_W']:.3f} W.",
            f"Q_total = {q:.3f} W; additional user duty multiplier = {margin:.3f}; sizing duty = {q_for_design:.3f} W.",
            f"ΔT_eff = LMTD × F = {dt:.4f} K.",
            f"Uo = 1 / sum(outside-area-referenced resistances) = {u:.3f} W/m²K.",
            f"Required area Areq = Q_sizing / (Uo·ΔT_eff) = {area_req:.4f} m².",
            f"Installed area Acalc = Nt·π·do·L = {installed_area:.4f} m²; area ratio = {area_ratio:.4f}.",
        ])
        return {
            "mode": mode, "exchanger": exchanger, "status": "PRELIMINARY RESULT", "errors": [], "warnings": warnings,
            "thermal": thermal, "required_duty_W": q, "design_duty_W": q_for_design,
            "required_area_m2": area_req, "installed_area_m2": installed_area,
            "tube_count_required": n, "tube_count_input": int(_v(g, "tube_count", 1)),
            "tube_od_mm": _v(g, "tube_od_mm", 19.0), "tube_id_mm": _v(g, "tube_id_mm", 16.0),
            "tube_length_m": _v(g, "tube_length_m", 3.0), "predicted_capacity_W": capacity,
            "process_dp": hydraulics["process_dp"], "hot_dp": hydraulics["hot_dp"],
            "capacity_ratio": capacity / max(q_for_design, 1e-12), "overdesign_percent": (area_ratio - 1.0) * 100.0,
            "recommended_geometry": recommended_g, "engineering_calculations": spec["metrics"],
            "preliminary_checks": checks, "calculation_trace": trace, "model_notes": ["Equipment-specific calculations use the equations and heuristics documented in the uploaded algorithm PDFs where reproducible; unreproducible or incomplete correlation substeps are flagged."]
        }

    # Rating: do not change installed geometry or silently increase shell/bundle dimensions.
    n = int(_v(g, "tube_count", 100))
    area = n * per_tube_area
    rating_g = dict(g)
    rating_g["auto_bundle_geometry"] = False
    local_p = dict(p)
    local_p["_effective_dt_K"] = dt
    spec = _specific_results(mode, local_p, rating_g, exchanger, n, area, q, False)
    u = spec["U_W_m2K"]
    area_req = q / max(u * dt, 1e-12)
    capacity = u * area * dt
    thermal["overall_U_W_m2K"] = u
    thermal["LMTD_K"] = dt
    thermal["raw_LMTD_K"] = dt / max(_v(p, "LMTD_correction_factor", 1.0), 1e-12)
    thermal["effective_temperature_difference_K"] = dt
    x_achieved = min(max((capacity - thermal["sensible_duty_W"]) / max(_v(p, "mass_flow_kg_s", 1.0) * _v(p, "latent_heat_kJ_kg", 2300.0) * 1000.0, 1e-12), 0.0), 1.0)
    hydraulics = _hydraulic_output(mode, p, rating_g, exchanger, n, spec["metrics"])
    warnings.extend(spec["warnings"])
    warnings.extend(hydraulics["warnings"])
    checks = _summarize_checks(exchanger, spec["metrics"], area / max(area_req, 1e-12), lower=AREA_LOWER, upper=upper, mode=mode)
    warnings.extend(checks["warnings"])
    adequate = capacity >= q_for_design
    if not adequate:
        warnings.append("Rating thermal gate failed: calculated capacity is below the requested duty (including any additional user duty multiplier).")
    trace.extend([
        f"Installed area Acalc = Nt·π·do·L = {area:.4f} m² (fixed rating geometry).",
        f"Q_required = {q:.3f} W; required area at calculated Uo = {area_req:.4f} m².",
        f"Uo = {u:.3f} W/m²K; ΔT_eff = {dt:.4f} K; Q_rating = Uo·Acalc·ΔT_eff = {capacity:.3f} W.",
        f"Capacity / target duty = {capacity / max(q_for_design, 1e-12):.4f}; thermal rating {'PASS' if adequate else 'FAIL'}.",
    ])
    return {
        "mode": mode, "exchanger": exchanger, "status": "PRELIMINARY RESULT", "errors": [], "warnings": list(dict.fromkeys(warnings)),
        "thermal": thermal, "target_duty_W": q_for_design, "required_duty_W": q,
        "required_area_m2": area_req, "available_area_m2": area, "installed_area_m2": area,
        "tube_count_input": n, "tube_od_mm": _v(g, "tube_od_mm", 19.0), "tube_id_mm": _v(g, "tube_id_mm", 16.0),
        "tube_length_m": _v(g, "tube_length_m", 3.0), "capacity_W": capacity,
        "predicted_capacity_W": capacity, "process_dp": hydraulics["process_dp"], "hot_dp": hydraulics["hot_dp"],
        "capacity_ratio": capacity / max(q_for_design, 1e-12), "achieved_vapor_fraction": x_achieved,
        "target_vapor_fraction": _v(p, "target_vapor_fraction", 0.2), "overdesign_percent": (capacity / max(q_for_design, 1e-12) - 1.0) * 100.0,
        "engineering_calculations": spec["metrics"], "preliminary_checks": checks, "calculation_trace": trace,
        "model_notes": ["Rating keeps the supplied tube count, tube sizes and shell dimensions fixed. A failing thermal or geometry check is reported, not automatically corrected."]
    }


def _hydraulic_output(mode: str, p: dict, g: dict, exchanger: str, n: int, metrics: dict) -> dict:
    from calculations.common.hydraulics import estimate_exchanger_pressure_drops
    warnings: list[str] = []
    if exchanger == "Forced Circulation Evaporator":
        dp = metrics.get("tube_friction_dp_kPa_estimate")
        u = metrics.get("tube_velocity_m_s")
        qpump = metrics.get("pump_flow_rate_m3_s")
        proc = {"delta_p_kPa": dp, "velocity_m_s": u, "Reynolds": metrics.get("tube_Reynolds"),
                "friction_factor": metrics.get("darcy_friction_factor_assumed"),
                "status": "single-phase Darcy screening; acceleration and two-phase effects omitted"}
        hot = estimate_exchanger_pressure_drops(p, g, n)["hot_dp"]
        if dp is not None and dp > _v(p, "allowable_process_dp_kPa", 100.0):
            warnings.append("Forced-circulation tube-side Darcy screening exceeds the entered allowable process-side pressure drop.")
        efficiency = _v(p, "pump_efficiency", 0.7)
        power = qpump * dp * 1000.0 / max(efficiency, 1e-12) if qpump and dp is not None else None
        metrics["pump_hydraulic_power_kW_estimate"] = power / 1000.0 if power is not None else None
        metrics["pump_efficiency_assumed"] = efficiency
        return {"process_dp": proc, "hot_dp": hot, "warnings": warnings}
    # A tube-channel Darcy proxy is intentionally not presented as a natural-loop/film/boiling result.
    hot = estimate_exchanger_pressure_drops(p, g, n)["hot_dp"]
    proc = {"delta_p_kPa": None, "velocity_m_s": None, "Reynolds": None, "friction_factor": None,
            "status": "not computed as a valid equipment-specific two-phase pressure drop; see the natural-circulation, dry-out or flooding checks"}
    warnings.append("A generic single-phase tube-side pressure-drop proxy is not shown as a true thermosyphon, pool-boiling or falling-film pressure drop.")
    if hot.get("delta_p_kPa") is not None and hot["delta_p_kPa"] > _v(p, "allowable_hot_dp_kPa", 100.0):
        warnings.append("Heating-side single-phase screening exceeds the entered allowable heating-side pressure drop.")
    return {"process_dp": proc, "hot_dp": hot, "warnings": warnings}


def _summarize_checks(exchanger: str, m: dict, area_ratio: float, lower: float, upper: float, mode: str = "Rating") -> dict:
    checks: dict[str, Any] = {"area_ratio": area_ratio, "area_ratio_lower_limit": lower, "area_ratio_upper_limit": upper,
                              "sizing_area_gate_applies": mode == "Sizing",
                              "sizing_area_gate_pass": (lower <= area_ratio <= upper) if mode == "Sizing" else None}
    warnings: list[str] = []
    if mode == "Sizing" and not lower <= area_ratio <= upper:
        warnings.append(f"Sizing area gate is outside the source algorithm's {lower:.2f}–{upper:.2f} installed/required area band.")
    if exchanger == "Falling Film Evaporator":
        checks["Palen_dryout_pass"] = m.get("Palen_dryout_pass")
        checks["minimum_wetting_pass"] = m.get("minimum_wetting_pass")
        checks["distributor_head_check_pass"] = m.get("distributor_head_check_pass")
        checks["Wallis_flooding_check_pass"] = m.get("Wallis_flooding_check_pass")
    if exchanger in {"Horizontal Thermosyphon Reboiler", "Vertical Thermosyphon Reboiler"}:
        checks["natural_loop_balance_pass"] = m.get("natural_loop_balance_pass")
    if exchanger in {"Horizontal Thermosyphon Reboiler", "Vertical Thermosyphon Reboiler", "Kettle Reboiler"}:
        checks["CHF_check_status"] = m.get("chf_check_status")
    if exchanger in {"Horizontal Thermosyphon Reboiler", "Kettle Reboiler"}:
        checks["shell_diameter_check_pass"] = m.get("shell_diameter_check_pass")
    checks["wall_thickness_check_status"] = m.get("wall_thickness_check_status")
    checks["warnings"] = warnings
    return checks
