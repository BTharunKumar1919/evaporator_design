"""Common router for equipment-specific sizing models."""
from __future__ import annotations
from calculations.common.engineering_models import run_equipment_calculation


def run_sizing(p: dict, g: dict, exchanger_name: str, model_notes=None, hydraulic_estimator=None) -> dict:
    # Keep the old adapter signature so external code using the starter API still works.
    return run_equipment_calculation("Sizing", p, g, exchanger_name)
