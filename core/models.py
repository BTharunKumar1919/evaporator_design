"""Canonical names and defaults for the evaporator-design starter project."""
from __future__ import annotations

EXCHANGERS = {
    "Falling Film Evaporator": "falling_film",
    "Forced Circulation Evaporator": "forced_circulation",
    "Vertical Thermosyphon Reboiler": "vertical_thermosyphon",
    "Horizontal Thermosyphon Reboiler": "horizontal_thermosyphon",
    "Kettle Reboiler": "kettle_reboiler",
}

DEFAULT_PROCESS_INPUTS = {
    # Generic thermal model inputs
    "mass_flow_kg_s": 1.0,
    "inlet_temperature_C": 25.0,
    "boiling_temperature_C": 80.0,
    "cp_kJ_kgK": 4.18,
    "latent_heat_kJ_kg": 2300.0,
    "target_vapor_fraction": 0.20,
    "hot_in_temperature_C": 120.0,
    "hot_out_temperature_C": 120.0,
    "overall_U_W_m2K": 1200.0,
    "LMTD_correction_factor": 1.0,
    "design_margin": 1.10,
    "process_density_kg_m3": 1000.0,
    "process_viscosity_Pa_s": 0.001,
    "allowable_process_dp_kPa": 100.0,
    "hot_mass_flow_kg_s": 0.50,
    "hot_density_kg_m3": 950.0,
    "hot_viscosity_Pa_s": 0.0002,
    "hot_hydraulic_diameter_m": 0.02,
    "hot_flow_area_m2": 0.05,
    "hot_flow_length_m": 2.0,
    "allowable_hot_dp_kPa": 100.0,
    # Selection-algorithm inputs
    "process_pressure_bar_abs": 3.5,
    "heating_pressure_bar_abs": 10.0,
    "critical_pressure_bar_abs": 0.0,  # zero disables near-critical gate until known
    "boiling_range_C": 6.5,
    "cold_fouling_factor_m2K_W": 0.0001,
    "hot_fouling_factor_m2K_W": 0.0002,
    "vertical_headroom_m": 6.0,
    "horizontal_floor_space_m": 6.0,
    "floor_space_restricted": False,
    "static_elevation_m": 1.8,
    "pump_permitted": True,
    "estimated_natural_loop_dp_kPa": None,
    "heat_sensitive": False,
    "thermally_unstable": False,
    "crystallizing_slurry": False,
    "fouling_or_solids": False,
    "high_heat_flux": False,
    "heating_medium_corrosive": False,
    "corrosive_toxic_process": False,
    "foaming": False,
    "natural_circulation_preferred": True,
}

DEFAULT_GEOMETRY = {
    "tube_count": 100,
    "tube_od_mm": 19.0,
    "tube_id_mm": 16.0,
    "tube_length_m": 3.0,
    "tube_passes": 2,
    "shell_diameter_m": 0.50,
    "bundle_diameter_m": 0.45,
    "baffle_spacing_m": 0.20,
    "liquid_level_m": 0.30,
    "circulation_ratio": 3.0,
    "static_elevation_m": 2.0,
}
