"""Basic input validation. Not a substitute for process/mechanical design review."""
from __future__ import annotations


def validate_process_inputs(p: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    positive = [
        ("mass_flow_kg_s", "Process mass flow"),
        ("cp_kJ_kgK", "Specific heat capacity"),
        ("latent_heat_kJ_kg", "Latent heat"),
        ("overall_U_W_m2K", "Overall heat-transfer coefficient"),
        ("LMTD_correction_factor", "LMTD correction factor"),
        ("process_density_kg_m3", "Process density"),
        ("process_viscosity_Pa_s", "Process viscosity"),
        ("hot_mass_flow_kg_s", "Heating-medium mass flow"),
        ("hot_density_kg_m3", "Heating-medium density"),
        ("hot_viscosity_Pa_s", "Heating-medium viscosity"),
        ("hot_hydraulic_diameter_m", "Heating-side hydraulic diameter"),
        ("hot_flow_area_m2", "Heating-side flow area"),
        ("hot_flow_length_m", "Heating-side flow length"),
    ]
    for key, label in positive:
        try:
            value = float(p[key])
            if value <= 0:
                errors.append(f"{label} must be greater than zero.")
        except (KeyError, TypeError, ValueError):
            errors.append(f"{label} is missing or not numeric.")

    x = float(p.get("target_vapor_fraction", -1))
    if not 0 <= x <= 1:
        errors.append("Target vapor fraction must lie between 0 and 1.")

    if float(p.get("design_margin", 0)) < 1:
        errors.append("Design margin must be at least 1.0.")
    if float(p.get("allowable_process_dp_kPa", 0)) <= 0:
        errors.append("Allowable process-side pressure drop must be greater than zero.")
    if float(p.get("allowable_hot_dp_kPa", 0)) <= 0:
        errors.append("Allowable heating-side pressure drop must be greater than zero.")

    if float(p.get("boiling_temperature_C", 0)) <= float(p.get("inlet_temperature_C", 0)):
        warnings.append(
            "Boiling temperature is not above the feed inlet temperature. The sensible-heating term is set to zero; check whether the feed is already hot or the temperatures are entered correctly."
        )
    if float(p.get("hot_in_temperature_C", 0)) <= float(p.get("boiling_temperature_C", 0)):
        errors.append("Heating-medium inlet temperature must be above the process boiling temperature for this preliminary model.")
    if float(p.get("hot_out_temperature_C", 0)) <= float(p.get("boiling_temperature_C", 0)):
        errors.append("Heating-medium outlet temperature must be above the process boiling temperature for this preliminary model.")
    if float(p.get("hot_out_temperature_C", 0)) > float(p.get("hot_in_temperature_C", 0)):
        warnings.append("Heating-medium outlet temperature exceeds its inlet temperature; verify the entered conditions.")
    return errors, warnings


def validate_geometry(g: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for key, label in [
        ("tube_count", "Tube count"),
        ("tube_od_mm", "Tube outside diameter"),
        ("tube_id_mm", "Tube inside diameter"),
        ("tube_length_m", "Tube length"),
        ("tube_passes", "Tube passes"),
        ("shell_diameter_m", "Shell diameter"),
        ("bundle_diameter_m", "Bundle diameter"),
    ]:
        try:
            if float(g[key]) <= 0:
                errors.append(f"{label} must be greater than zero.")
        except (KeyError, TypeError, ValueError):
            errors.append(f"{label} is missing or not numeric.")
    if float(g.get("tube_id_mm", 0)) >= float(g.get("tube_od_mm", 0)):
        errors.append("Tube inside diameter must be smaller than tube outside diameter.")
    if float(g.get("bundle_diameter_m", 0)) > float(g.get("shell_diameter_m", 0)):
        warnings.append("Bundle diameter exceeds shell diameter; review clearances and layout.")
    if int(g.get("tube_count", 1)) < int(g.get("tube_passes", 1)):
        warnings.append("Tube count is smaller than the number of passes; check the tube layout.")
    if float(g.get("circulation_ratio", 1)) < 1:
        warnings.append("Circulation ratio is below 1.0; verify the definition used for your process.")
    return errors, warnings
