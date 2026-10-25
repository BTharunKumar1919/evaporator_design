"""Sizing entry point for Vertical Thermosyphon Reboiler."""
from calculations.common.sizing import run_sizing

EXCHANGER_NAME = 'Vertical Thermosyphon Reboiler'

def size(process_inputs: dict, geometry: dict) -> dict:
    return run_sizing(process_inputs, geometry, EXCHANGER_NAME)
