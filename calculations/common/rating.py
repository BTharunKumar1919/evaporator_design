"""Common router for equipment-specific rating models."""
from __future__ import annotations
from calculations.common.engineering_models import run_equipment_calculation


def run_rating(p: dict, g: dict, exchanger_name: str, model_notes=None, hydraulic_estimator=None) -> dict:
    # Rating preserves user-supplied geometry; the equipment-specific model reports failed gates.
    return run_equipment_calculation("Rating", p, g, exchanger_name)
