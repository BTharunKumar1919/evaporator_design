"""Routes a request to the selected exchanger's sizing or rating function."""
from __future__ import annotations
from core.models import EXCHANGERS
from calculations.evaporators.falling_film.sizing import size as size_falling
from calculations.evaporators.falling_film.rating import rate as rate_falling
from calculations.evaporators.forced_circulation.sizing import size as size_forced
from calculations.evaporators.forced_circulation.rating import rate as rate_forced
from calculations.evaporators.vertical_thermosyphon.sizing import size as size_vertical
from calculations.evaporators.vertical_thermosyphon.rating import rate as rate_vertical
from calculations.evaporators.horizontal_thermosyphon.sizing import size as size_horizontal
from calculations.evaporators.horizontal_thermosyphon.rating import rate as rate_horizontal
from calculations.evaporators.kettle_reboiler.sizing import size as size_kettle
from calculations.evaporators.kettle_reboiler.rating import rate as rate_kettle

ROUTES = {
    "falling_film": (size_falling, rate_falling),
    "forced_circulation": (size_forced, rate_forced),
    "vertical_thermosyphon": (size_vertical, rate_vertical),
    "horizontal_thermosyphon": (size_horizontal, rate_horizontal),
    "kettle_reboiler": (size_kettle, rate_kettle),
}


def calculate(mode: str, exchanger_name: str, process_inputs: dict, geometry: dict) -> dict:
    """Run the exchanger-specific adapter for mode 'Sizing' or 'Rating'."""
    if exchanger_name not in EXCHANGERS:
        raise ValueError(f"Unknown exchanger type: {exchanger_name}")
    module_key = EXCHANGERS[exchanger_name]
    if module_key not in ROUTES:
        raise ValueError(f"No calculation route configured for {exchanger_name}")
    sizing_fn, rating_fn = ROUTES[module_key]
    if mode == "Sizing":
        return sizing_fn(process_inputs, geometry)
    if mode == "Rating":
        return rating_fn(process_inputs, geometry)
    raise ValueError("Mode must be 'Sizing' or 'Rating'.")
