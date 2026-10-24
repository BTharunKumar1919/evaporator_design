"""Sizing entry point for Vertical Thermosyphon Reboiler."""
from calculations.common.sizing import run_sizing
from .hydraulics import estimate_pressure_drops, MODEL_NOTES
from .checks import run_checks

EXCHANGER_NAME = 'Vertical Thermosyphon Reboiler'

def size(process_inputs: dict, geometry: dict) -> dict:
    result = run_sizing(process_inputs, geometry, EXCHANGER_NAME, MODEL_NOTES, estimate_pressure_drops)
    result["preliminary_checks"] = run_checks(process_inputs, geometry)
    return result
