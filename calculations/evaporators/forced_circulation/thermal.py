"""Thermal-model notes and common preliminary calculation adapter for Forced Circulation Evaporator."""
from calculations.common.thermal import calculate_thermal_basis

MODEL_NOTES = ['PLACEHOLDER: circulation-loop momentum balance, pump curve, two-phase friction, and flashing effects are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is a single-phase equivalent tube-flow proxy; pump sizing is not included.']

def thermal_basis(process_inputs: dict) -> dict:
    """Return the current common thermal basis; exchanger-specific correlations remain TODO."""
    result = calculate_thermal_basis(process_inputs)
    result["model_notes"] = list(MODEL_NOTES)
    return result
