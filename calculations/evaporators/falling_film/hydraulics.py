"""Hydraulic adapter for Falling Film Evaporator; uses a deliberately rough Darcy proxy."""
from calculations.common.hydraulics import estimate_exchanger_pressure_drops

MODEL_NOTES = ['PLACEHOLDER: film wetting, distributor performance, film thickness, and film-side boiling correlations are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is an equivalent tube-flow proxy, not a falling-film hydraulic model.']

def estimate_pressure_drops(process_inputs: dict, geometry: dict, tube_count: int | None = None) -> dict:
    result = estimate_exchanger_pressure_drops(process_inputs, geometry, tube_count)
    result["model_notes"] = list(MODEL_NOTES)
    return result
