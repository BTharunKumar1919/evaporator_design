"""Preliminary validation/check adapters for Horizontal Thermosyphon Reboiler."""
from core.validation import validate_process_inputs, validate_geometry

MODEL_NOTES = ['PLACEHOLDER: horizontal thermosyphon circulation, two-phase boiling, and shell/tube-side distribution correlations are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is not a thermosyphon circulation pressure-drop solution.']

def run_checks(process_inputs: dict, geometry: dict) -> dict:
    process_errors, process_warnings = validate_process_inputs(process_inputs)
    geometry_errors, geometry_warnings = validate_geometry(geometry)
    return {
        "errors": process_errors + geometry_errors,
        "warnings": process_warnings + geometry_warnings + list(MODEL_NOTES),
        "scope": "Starter checks only; no code/standard-based mechanical or two-phase design verification.",
    }
