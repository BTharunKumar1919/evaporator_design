"""Transparent rule-based equipment selection for preliminary evaporator sizing.

Rules follow the team's uploaded selection-algorithm document. Scores rank the
remaining options; the user always confirms/overrides the recommendation.
This is a coursework prototype, not a validated industrial design tool.
"""
from __future__ import annotations
from math import isfinite

NAMES = [
    "Falling Film Evaporator",
    "Forced Circulation Evaporator",
    "Vertical Thermosyphon Reboiler",
    "Horizontal Thermosyphon Reboiler",
    "Kettle Reboiler",
]
FORCED = "Forced Circulation Evaporator"
FALLING = "Falling Film Evaporator"
VERTICAL = "Vertical Thermosyphon Reboiler"
HORIZONTAL = "Horizontal Thermosyphon Reboiler"
KETTLE = "Kettle Reboiler"


def preprocess_selection_inputs(p: dict) -> dict:
    """Calculate the five pre-processing values described in the uploaded PDF.

    All pressure values are absolute bar unless the key explicitly says kPa.
    """
    mdot = float(p.get("mass_flow_kg_s", 0.0))
    x = float(p.get("target_vapor_fraction", 0.0))
    cp = float(p.get("cp_kJ_kgK", 0.0)) * 1000.0
    hfg = float(p.get("latent_heat_kJ_kg", 0.0)) * 1000.0
    tb = float(p.get("boiling_temperature_C", 0.0))
    tin = float(p.get("inlet_temperature_C", 0.0))
    th_in = float(p.get("hot_in_temperature_C", 0.0))
    th_out = float(p.get("hot_out_temperature_C", 0.0))
    rho_l = float(p.get("process_density_kg_m3", 0.0))
    hstat = float(p.get("static_elevation_m", 0.0))
    vapor_rate_override = _get(p, "vaporization_rate_kg_s", 0.0)
    vapor_rate = vapor_rate_override if vapor_rate_override > 0 else mdot * x
    recirculation_ratio = (1.0 - x) / x if x > 0 else None
    sensible = mdot * cp * max(tb - tin, 0.0)
    latent = vapor_rate * hfg
    duty = sensible + latent
    t_mean = (th_in + th_out) / 2.0
    dt_eff = t_mean - tb
    static_head_kpa = rho_l * 9.81 * hstat / 1000.0
    return {
        "exit_vapor_fraction_xe": x,
        "vapor_rate_kg_s": vapor_rate,
        "vapor_rate_override_used": vapor_rate_override > 0,
        "recirculation_ratio_R": recirculation_ratio,
        "sensible_duty_kW": sensible / 1000.0,
        "latent_duty_kW": latent / 1000.0,
        "total_duty_kW": duty / 1000.0,
        "heating_mean_temperature_C": t_mean,
        "effective_temperature_approach_C": dt_eff,
        "available_static_head_kPa": static_head_kpa,
    }


def _get(p: dict, key: str, default=0.0) -> float:
    try:
        value = float(p.get(key, default))
        return value if isfinite(value) else float(default)
    except (TypeError, ValueError):
        return float(default)


def recommend_equipment(p: dict) -> list[dict]:
    """Apply priority gates, then rank candidates and return a readable trace.

    The algorithm follows the uploaded justification deck's thresholds. The
    hydraulic validation remains provisional unless a user supplies an estimate
    of frictional + acceleration pressure loss for the natural-circulation loop.
    """
    d = preprocess_selection_inputs(p)
    scores = {name: 0 for name in NAMES}
    reasons = {name: [] for name in NAMES}
    hard_blocked: dict[str, list[str]] = {name: [] for name in NAMES}
    trace: list[str] = []
    flags: list[str] = []

    mu_cp = _get(p, "process_viscosity_Pa_s", 0.001) * 1000.0  # Pa.s -> cP (numerically mPa.s)
    rf_c = _get(p, "cold_fouling_factor_m2K_W", 0.0001)
    boiling_range = _get(p, "boiling_range_C", 0.0)
    pc = _get(p, "process_pressure_bar_abs", 1.0)
    pcrit = _get(p, "critical_pressure_bar_abs", 0.0)
    near_critical = pcrit > 0 and pc >= 0.7 * pcrit
    deep_vacuum = pc <= 0.15
    x = d["exit_vapor_fraction_xe"]
    dt = d["effective_temperature_approach_C"]
    q_mw = d["total_duty_kW"] / 1000.0
    headroom = _get(p, "vertical_headroom_m", 6.0)
    floor_restricted = bool(p.get("floor_space_restricted", False))
    static_head = _get(p, "static_elevation_m", 0.0)
    pump_allowed = bool(p.get("pump_permitted", True))
    loop_dp = p.get("estimated_natural_loop_dp_kPa")
    loop_dp = None if loop_dp in (None, "", "Not provided") else _get(p, "estimated_natural_loop_dp_kPa", 0.0)
    allow_dp = _get(p, "allowable_process_dp_kPa", 100.0)

    trace.append("PRE-PROCESSING")
    trace.append(f"Exit vapor mass fraction xe = {x:.3f}; vapor generation rate = {d['vapor_rate_kg_s']:.4g} kg/s" + (" (independent override)." if d.get("vapor_rate_override_used") else " (feed flow × xe)."))
    trace.append("Recirculation ratio R = (1 - xe)/xe = " + (f"{d['recirculation_ratio_R']:.3f}." if d['recirculation_ratio_R'] is not None else "undefined at xe = 0."))
    trace.append(f"Duty estimate Q = sensible + latent = {d['total_duty_kW']:.2f} kW ({q_mw:.3f} MW).")
    trace.append(f"Effective temperature approach ΔTeff = mean heating temperature - process boiling temperature = {dt:.2f} °C.")
    trace.append(f"Available static head ΔPstatic = rho*g*H = {d['available_static_head_kPa']:.2f} kPa.")
    if deep_vacuum and d["recirculation_ratio_R"] is not None and not (10.0 <= d["recirculation_ratio_R"] <= 25.0):
        trace.append(f"SOURCE CONSISTENCY WARNING: deep-vacuum case has R = {d['recirculation_ratio_R']:.2f}, outside the justification deck's stated aqueous/vacuum guidance of roughly 10–25. The worked example itself uses xe = 0.25 (R = 3), so confirm which criterion your instructor expects.")

    # Gate 1: high viscosity, slurry/crystallizing, heavy fouling, or high heat flux.
    gate1_reasons = []
    if mu_cp >= 50: gate1_reasons.append(f"viscosity {mu_cp:.1f} cP >= 50 cP")
    if p.get("crystallizing_slurry", False): gate1_reasons.append("crystallizing/slurry service")
    if rf_c >= 0.0004: gate1_reasons.append(f"cold-side fouling factor {rf_c:g} >= 0.0004 m²·K/W")
    if p.get("high_heat_flux", False): gate1_reasons.append("high heat-flux flag")
    if gate1_reasons:
        trace.append("GATE 1: TRIGGERED — " + "; ".join(gate1_reasons) + ". Forced circulation is the priority recommendation.")
        scores[FORCED] += 12; reasons[FORCED].extend(gate1_reasons)
        for name in [FALLING, VERTICAL, HORIZONTAL, KETTLE]:
            scores[name] -= 4
            hard_blocked[name].append("Gate 1 indicates forced circulation should be prioritised; alternatives require explicit engineering review.")
    else:
        trace.append("GATE 1: not triggered — proceed to Gate 2.")

    # Gate 2: thermal sensitivity or low driving temperature difference.
    gate1 = bool(gate1_reasons)
    gate2 = bool(p.get("heat_sensitive", False) or p.get("thermally_unstable", False) or dt <= 8.0)
    if gate2 and not gate1:
        why = []
        if p.get("heat_sensitive", False) or p.get("thermally_unstable", False): why.append("heat-sensitive/thermally unstable product")
        if dt <= 8.0: why.append(f"ΔTeff {dt:.2f} °C <= 8 °C")
        if headroom >= 4.5:
            scores[FALLING] += 10; reasons[FALLING].extend(why + [f"vertical headroom {headroom:.2f} m >= 4.5 m"])
            trace.append("GATE 2: TRIGGERED — " + "; ".join(why) + f". Headroom {headroom:.2f} m >= 4.5 m: Falling Film prioritised.")
            scores[HORIZONTAL] += 4; reasons[HORIZONTAL].append("horizontal forced-circulation fallback if falling-film layout is unsuitable")
        else:
            scores[FORCED] += 8; reasons[FORCED].extend(why + [f"headroom {headroom:.2f} m < 4.5 m; horizontal forced-circulation fallback"])
            trace.append("GATE 2: TRIGGERED — " + "; ".join(why) + f". Headroom {headroom:.2f} m < 4.5 m: horizontal forced circulation prioritised.")
            scores[HORIZONTAL] += 8; reasons[HORIZONTAL].append("horizontal configuration fallback for restricted headroom/low ΔT")
        for name in [VERTICAL, KETTLE]:
            scores[name] -= 2
            hard_blocked[name].append("Gate 2 prefers low-holdup/low-approach equipment; confirm suitability before selecting this alternative.")
    else:
        if gate1:
            trace.append("GATE 2: skipped because Gate 1 already triggered the priority Forced Circulation route.")
        else:
            trace.append("GATE 2: not triggered — proceed to Gate 3.")

    # Gate 3: high vapor fraction or extreme pressure.
    gate3_reasons = []
    if x >= 0.35: gate3_reasons.append(f"xe {x:.3f} >= 0.35")
    if near_critical: gate3_reasons.append(f"process pressure {pc:.3g} bar >= 0.7 Pcrit ({0.7*pcrit:.3g} bar)")
    if deep_vacuum: gate3_reasons.append(f"deep vacuum: process pressure {pc:.3g} bar <= 0.15 bar abs")
    if gate3_reasons and not gate1 and not gate2:
        if rf_c <= 0.0002 and boiling_range < 10.0:
            scores[KETTLE] += 10; reasons[KETTLE].extend(gate3_reasons + ["cold-side fouling <= 0.0002 m²·K/W and boiling range < 10 °C"])
            trace.append("GATE 3: TRIGGERED — " + "; ".join(gate3_reasons) + ". Cleanliness and boiling-range checks pass: Kettle prioritised.")
            for name in [VERTICAL, HORIZONTAL]:
                scores[name] -= 4
                hard_blocked[name].append("Extreme pressure/vapor-fraction gate prioritises kettle or forced circulation over thermosyphon.")
        else:
            scores[FORCED] += 10; reasons[FORCED].extend(gate3_reasons + ["kettle sub-gate failed: fouling factor > 0.0002 or boiling range >= 10 °C"])
            trace.append("GATE 3: TRIGGERED — " + "; ".join(gate3_reasons) + ". Kettle cleanliness/boiling-range sub-gate fails: Forced Circulation prioritised.")
            scores[KETTLE] -= 5
            hard_blocked[KETTLE].append("Kettle sub-gate fails: cold-side fouling must be <= 0.0002 m²·K/W and boiling range < 10 °C.")
    else:
        if gate1 or gate2:
            trace.append("GATE 3: skipped because a higher-priority gate already selected the preferred equipment class.")
        else:
            trace.append("GATE 3: not triggered — evaluate natural-circulation hydraulic loop.")

    # Natural circulation loop A: do not fabricate a pressure-drop result.
    gate3 = bool(gate3_reasons) and not gate1 and not gate2
    if not gate1 and not gate2 and not gate3:
        if not pump_allowed:
            trace.append("HYDRAULIC LOOP A: pump is not permitted; natural circulation is preferred, but feasibility is not confirmed without a loop ΔP estimate.")
        else:
            trace.append("HYDRAULIC LOOP A: natural-circulation candidates may be compared with forced circulation; pump is permitted.")
        if loop_dp is None:
            trace.append("Natural-loop pressure drop was not supplied: feasibility is UNKNOWN, not assumed TRUE.")
            for name in [VERTICAL, HORIZONTAL]:
                scores[name] += 2; reasons[name].append("candidate for natural circulation; loop hydraulic feasibility still needs validation")
        else:
            feasible = d["available_static_head_kPa"] >= loop_dp and loop_dp <= allow_dp
            trace.append(f"Natural-loop check: ΔPstatic {d['available_static_head_kPa']:.2f} kPa vs estimated loop loss {loop_dp:.2f} kPa; allowable process ΔP {allow_dp:.2f} kPa -> {'PASS' if feasible else 'FAIL'}.")
            if feasible:
                for name in [VERTICAL, HORIZONTAL]:
                    scores[name] += 5; reasons[name].append("estimated natural-loop pressure loss is within available head and allowable ΔP")
            else:
                scores[FORCED] += 8; reasons[FORCED].append("natural-circulation hydraulic check failed; forced circulation fallback")
                for name in [VERTICAL, HORIZONTAL]:
                    scores[name] -= 5
                    hard_blocked[name].append("Estimated natural-loop pressure loss exceeds available static head or allowable pressure drop.")

        # Gate 4 geometry split applies only to natural-circulation candidates.
        if headroom < 4.5 or q_mw >= 10.0:
            scores[HORIZONTAL] += 5
            reasons[HORIZONTAL].append("Gate 4: restricted vertical headroom or duty >= 10 MW")
            trace.append(f"GATE 4: horizontal thermosyphon favoured (headroom {headroom:.2f} m < 4.5 m or duty {q_mw:.3f} MW >= 10 MW).")
        elif floor_restricted and static_head >= 1.2:
            scores[VERTICAL] += 5
            reasons[VERTICAL].append("Gate 4: restricted floor space and static head >= 1.2 m")
            trace.append("GATE 4: vertical thermosyphon favoured (restricted floor space and static head >= 1.2 m).")
        else:
            scores[HORIZONTAL] += 1; scores[VERTICAL] += 1
            reasons[HORIZONTAL].append("Gate 4: general horizontal candidate")
            reasons[VERTICAL].append("Gate 4: general vertical candidate")
            trace.append("GATE 4: no strong geometry preference; both thermosyphon orientations remain candidates.")

    # Pump constraint: forced circulation cannot be recommended as feasible if no pump.
    if not pump_allowed:
        hard_blocked[FORCED].append("Pump is not permitted by the entered plant constraint.")
        scores[FORCED] -= 3
        trace.append("PUMP CONSTRAINT: forced circulation penalised because a pump is not permitted; verify whether the stated constraint is absolute.")

    # Side allocation based on the uploaded fluid-allocation matrix.
    corrosive_heating = bool(p.get("heating_medium_corrosive", False))
    allocations = {
        FALLING: ("Boiling process fluid (downward film)", "Heating medium / condensing steam"),
        FORCED: ("Pumped boiling process fluid", "Heating medium"),
        VERTICAL: ("Boiling process fluid (upward tube-side flow)", "Heating medium (shell side), unless corrosive override applies"),
        HORIZONTAL: ("Heating medium (tube side)", "Boiling process fluid (shell-side cross-flow)"),
        KETTLE: ("Heating medium (tube bundle)", "Boiling process fluid (pool boiling in K-shell)"),
    }
    if corrosive_heating:
        trace.append("ALLOCATION OVERRIDE: heating medium marked corrosive. Confirm metallurgy and the source algorithm's corrosion override before finalising side allocation.")
        allocations[VERTICAL] = ("Corrosive heating medium (tube side)", "Boiling process fluid (shell side; special internals may be needed)")

    ranked = sorted(NAMES, key=lambda n: (scores[n], -NAMES.index(n)), reverse=True)
    results = []
    for i, name in enumerate(ranked, start=1):
        results.append({
            "rank": i,
            "exchanger": name,
            "score": scores[name],
            "reasons": reasons[name] or ["No strong rule matched; retained for user consideration."],
            "status": "REVIEW REQUIRED" if hard_blocked[name] else "CANDIDATE",
            "cautions": hard_blocked[name],
            "tube_side": allocations[name][0],
            "shell_side": allocations[name][1],
        })
    # Return trace and preprocessed values via function attributes for backwards compatibility
    # with the original GUI's simple list return contract.
    recommend_equipment.last_trace = trace
    recommend_equipment.last_preprocessing = d
    recommend_equipment.last_flags = {
        "gate1_triggered": bool(gate1_reasons), "gate2_triggered": gate2,
        "gate3_triggered": bool(gate3_reasons), "near_critical": near_critical,
        "deep_vacuum": deep_vacuum, "natural_loop_dp_kPa": loop_dp,
    }
    return results


recommend_equipment.last_trace = []
recommend_equipment.last_preprocessing = {}
recommend_equipment.last_flags = {}
