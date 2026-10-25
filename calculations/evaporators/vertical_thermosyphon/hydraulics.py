"""Hydraulic result adapter for Vertical Thermosyphon Reboiler; use the algorithm-specific checks in the central model."""
from calculations.common.engineering_models import run_equipment_calculation

EXCHANGER_NAME = 'Vertical Thermosyphon Reboiler'
MODEL_NOTES = ["Hydraulic results are preliminary. The model deliberately does not label a generic single-phase estimate as a full two-phase loop solution."]

def estimate_pressure_drops(process_inputs: dict, geometry: dict, tube_count: int | None = None, mode: str = "Rating") -> dict:
    g = dict(geometry)
    if tube_count is not None:
        g["tube_count"] = int(tube_count)
    result = run_equipment_calculation(mode, process_inputs, g, EXCHANGER_NAME)
    return {"process_dp": result.get("process_dp", {}), "hot_dp": result.get("hot_dp", {}),
            "engineering_calculations": result.get("engineering_calculations", {}),
            "model_notes": list(MODEL_NOTES), "warnings": result.get("warnings", [])}
