"""Rating entry point for Falling Film Evaporator."""
from calculations.common.rating import run_rating
from .hydraulics import estimate_pressure_drops, MODEL_NOTES
from .checks import run_checks

EXCHANGER_NAME = 'Falling Film Evaporator'

def rate(process_inputs: dict, geometry: dict) -> dict:
    result = run_rating(process_inputs, geometry, EXCHANGER_NAME, MODEL_NOTES, estimate_pressure_drops)
    result["preliminary_checks"] = run_checks(process_inputs, geometry)
    return result
