"""Hydraulic adapter for Forced Circulation Evaporator; uses a deliberately rough Darcy proxy."""
from calculations.common.hydraulics import estimate_exchanger_pressure_drops

MODEL_NOTES = ['PLACEHOLDER: circulation-loop momentum balance, pump curve, two-phase friction, and flashing effects are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is a single-phase equivalent tube-flow proxy; pump sizing is not included.']

def estimate_pressure_drops(process_inputs: dict, geometry: dict, tube_count: int | None = None) -> dict:
    result = estimate_exchanger_pressure_drops(process_inputs, geometry, tube_count)
    result["model_notes"] = list(MODEL_NOTES)
    return result
