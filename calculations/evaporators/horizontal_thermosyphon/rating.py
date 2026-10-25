"""Rating entry point for Horizontal Thermosyphon Reboiler."""
from calculations.common.rating import run_rating

EXCHANGER_NAME = 'Horizontal Thermosyphon Reboiler'

def rate(process_inputs: dict, geometry: dict) -> dict:
    return run_rating(process_inputs, geometry, EXCHANGER_NAME)
