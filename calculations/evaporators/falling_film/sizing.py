"""Sizing entry point for Falling Film Evaporator."""
from calculations.common.sizing import run_sizing

EXCHANGER_NAME = 'Falling Film Evaporator'

def size(process_inputs: dict, geometry: dict) -> dict:
    return run_sizing(process_inputs, geometry, EXCHANGER_NAME)
