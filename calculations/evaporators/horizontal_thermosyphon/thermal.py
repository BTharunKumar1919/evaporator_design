"""Thermal result adapter for Horizontal Thermosyphon Reboiler; shares the active source-aligned calculation engine."""
from calculations.common.engineering_models import run_equipment_calculation

EXCHANGER_NAME = 'Horizontal Thermosyphon Reboiler'

def thermal_basis(process_inputs: dict, geometry: dict | None = None, mode: str = "Rating") -> dict:
    result = run_equipment_calculation(mode, process_inputs, geometry or {}, EXCHANGER_NAME)
    return result.get("thermal", {}) | {"engineering_calculations": result.get("engineering_calculations", {}),
                                      "warnings": result.get("warnings", [])}
