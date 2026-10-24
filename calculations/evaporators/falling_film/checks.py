"""Preliminary validation/check adapters for Falling Film Evaporator."""
from core.validation import validate_process_inputs, validate_geometry

MODEL_NOTES = ['PLACEHOLDER: film wetting, distributor performance, film thickness, and film-side boiling correlations are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is an equivalent tube-flow proxy, not a falling-film hydraulic model.']

def run_checks(process_inputs: dict, geometry: dict) -> dict:
    process_errors, process_warnings = validate_process_inputs(process_inputs)
    geometry_errors, geometry_warnings = validate_geometry(geometry)
    return {
        "errors": process_errors + geometry_errors,
        "warnings": process_warnings + geometry_warnings + list(MODEL_NOTES),
        "scope": "Starter checks only; no code/standard-based mechanical or two-phase design verification.",
    }
