"""Rating entry point for Falling Film Evaporator."""
from calculations.common.rating import run_rating

EXCHANGER_NAME = 'Falling Film Evaporator'

def rate(process_inputs: dict, geometry: dict) -> dict:
    return run_rating(process_inputs, geometry, EXCHANGER_NAME)
