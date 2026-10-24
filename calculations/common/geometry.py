"""Geometry helpers shared by the preliminary evaporator modules."""
from __future__ import annotations
import math
from core.unit_conversion import mm_to_m


def external_tube_area_m2(tube_count: int, tube_od_mm: float, tube_length_m: float) -> float:
    return int(tube_count) * math.pi * mm_to_m(tube_od_mm) * float(tube_length_m)


def tube_count_for_area(area_required_m2: float, tube_od_mm: float, tube_length_m: float) -> int:
    area_per_tube = math.pi * mm_to_m(tube_od_mm) * float(tube_length_m)
    if area_per_tube <= 0:
        raise ValueError("Tube diameter and length must be positive.")
    return max(1, int(math.ceil(float(area_required_m2) / area_per_tube)))


def tube_side_flow_area_m2(tube_count: int, tube_id_mm: float, passes: int = 1) -> float:
    tubes_per_pass = max(1.0, float(tube_count) / max(1, int(passes)))
    return tubes_per_pass * math.pi * mm_to_m(tube_id_mm) ** 2 / 4.0
