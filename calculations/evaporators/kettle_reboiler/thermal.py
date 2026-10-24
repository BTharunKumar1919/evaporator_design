"""Thermal-model notes and common preliminary calculation adapter for Kettle Reboiler."""
from calculations.common.thermal import calculate_thermal_basis

MODEL_NOTES = ['PLACEHOLDER: pool-boiling correlation, bundle inundation, vapor disengagement, liquid level, and entrainment checks are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side proxy does not model pool boiling or vapor-space pressure loss.']

def thermal_basis(process_inputs: dict) -> dict:
    """Return the current common thermal basis; exchanger-specific correlations remain TODO."""
    result = calculate_thermal_basis(process_inputs)
    result["model_notes"] = list(MODEL_NOTES)
    return result
