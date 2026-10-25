"""Sizing entry point for Kettle Reboiler."""
from calculations.common.sizing import run_sizing

EXCHANGER_NAME = 'Kettle Reboiler'

def size(process_inputs: dict, geometry: dict) -> dict:
    return run_sizing(process_inputs, geometry, EXCHANGER_NAME)
