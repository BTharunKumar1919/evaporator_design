"""Hydraulic adapter for Kettle Reboiler; uses a deliberately rough Darcy proxy."""
from calculations.common.hydraulics import estimate_exchanger_pressure_drops

MODEL_NOTES = ['PLACEHOLDER: pool-boiling correlation, bundle inundation, vapor disengagement, liquid level, and entrainment checks are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side proxy does not model pool boiling or vapor-space pressure loss.']

def estimate_pressure_drops(process_inputs: dict, geometry: dict, tube_count: int | None = None) -> dict:
    result = estimate_exchanger_pressure_drops(process_inputs, geometry, tube_count)
    result["model_notes"] = list(MODEL_NOTES)
    return result
