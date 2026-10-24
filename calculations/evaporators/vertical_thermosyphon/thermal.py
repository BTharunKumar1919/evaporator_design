"""Thermal-model notes and common preliminary calculation adapter for Vertical Thermosyphon Reboiler."""
from calculations.common.thermal import calculate_thermal_basis

MODEL_NOTES = ['PLACEHOLDER: natural-circulation iteration, two-phase void fraction, static head, and circulation stability are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is not a thermosyphon circulation pressure-drop solution.']

def thermal_basis(process_inputs: dict) -> dict:
    """Return the current common thermal basis; exchanger-specific correlations remain TODO."""
    result = calculate_thermal_basis(process_inputs)
    result["model_notes"] = list(MODEL_NOTES)
    return result
