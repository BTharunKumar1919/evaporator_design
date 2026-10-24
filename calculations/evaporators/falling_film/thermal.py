"""Thermal-model notes and common preliminary calculation adapter for Falling Film Evaporator."""
from calculations.common.thermal import calculate_thermal_basis

MODEL_NOTES = ['PLACEHOLDER: film wetting, distributor performance, film thickness, and film-side boiling correlations are not implemented.', 'PRESSURE-DROP LIMITATION: the process-side result is an equivalent tube-flow proxy, not a falling-film hydraulic model.']

def thermal_basis(process_inputs: dict) -> dict:
    """Return the current common thermal basis; exchanger-specific correlations remain TODO."""
    result = calculate_thermal_basis(process_inputs)
    result["model_notes"] = list(MODEL_NOTES)
    return result
