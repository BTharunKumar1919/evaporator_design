"""Compatibility adapter exposing check results from the central Kettle Reboiler model."""
from calculations.common.engineering_models import run_equipment_calculation

EXCHANGER_NAME = 'Kettle Reboiler'

def run_checks(process_inputs: dict, geometry: dict, mode: str = "Rating") -> dict:
    result = run_equipment_calculation(mode, process_inputs, geometry, EXCHANGER_NAME)
    return {"errors": result.get("errors", []), "warnings": result.get("warnings", []),
            "checks": result.get("preliminary_checks", {}),
            "engineering_calculations": result.get("engineering_calculations", {}),
            "scope": "Source-aligned preliminary checks; detailed vendor/TEMA/ASME and two-phase verification remains required."}
