"""Rating entry point for Horizontal Thermosyphon Reboiler."""
from calculations.common.rating import run_rating
from .hydraulics import estimate_pressure_drops, MODEL_NOTES
from .checks import run_checks

EXCHANGER_NAME = 'Horizontal Thermosyphon Reboiler'

def rate(process_inputs: dict, geometry: dict) -> dict:
    result = run_rating(process_inputs, geometry, EXCHANGER_NAME, MODEL_NOTES, estimate_pressure_drops)
    result["preliminary_checks"] = run_checks(process_inputs, geometry)
    return result
