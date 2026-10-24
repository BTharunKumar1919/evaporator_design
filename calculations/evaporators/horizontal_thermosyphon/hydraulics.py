"""Hydraulic adapter for Horizontal Thermosyphon Reboiler; uses a deliberately rough Darcy proxy."""
from calculations.common.hydraulics import estimate_exchanger_pressure_drops

MODEL_NOTES = ['PLACEHOLDER: horizontal thermosyphon circulation, two-phase boiling, and shell/tube-side distribution correlations are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is not a thermosyphon circulation pressure-drop solution.']

def estimate_pressure_drops(process_inputs: dict, geometry: dict, tube_count: int | None = None) -> dict:
    result = estimate_exchanger_pressure_drops(process_inputs, geometry, tube_count)
    result["model_notes"] = list(MODEL_NOTES)
    return result
