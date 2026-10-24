"""Preliminary validation/check adapters for Forced Circulation Evaporator."""
from core.validation import validate_process_inputs, validate_geometry

MODEL_NOTES = ['PLACEHOLDER: circulation-loop momentum balance, pump curve, two-phase friction, and flashing effects are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is a single-phase equivalent tube-flow proxy; pump sizing is not included.']

def run_checks(process_inputs: dict, geometry: dict) -> dict:
    process_errors, process_warnings = validate_process_inputs(process_inputs)
    geometry_errors, geometry_warnings = validate_geometry(geometry)
    return {
        "errors": process_errors + geometry_errors,
        "warnings": process_warnings + geometry_warnings + list(MODEL_NOTES),
        "scope": "Starter checks only; no code/standard-based mechanical or two-phase design verification.",
    }
