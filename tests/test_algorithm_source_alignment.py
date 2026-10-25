"""Regression tests for source-derived equations and equipment-specific paths."""
from copy import deepcopy
import math

from calculations.common.thermal import calculate_thermal_basis
from core.equipment_selection import recommend_equipment, preprocess_selection_inputs
from core.models import DEFAULT_GEOMETRY, DEFAULT_PROCESS_INPUTS, EXCHANGERS
from core.solver import calculate


def _forced_circ_example_inputs():
    p = deepcopy(DEFAULT_PROCESS_INPUTS)
    p.update({
        "mass_flow_kg_s": 10.0,
        "inlet_temperature_C": 80.0,
        "boiling_temperature_C": 100.0,
        "cp_kJ_kgK": 4.18,
        "latent_heat_kJ_kg": 2260.0,
        "target_vapor_fraction": 0.10,
        "hot_in_temperature_C": 120.0,
        "hot_out_temperature_C": 120.0,
        "process_density_kg_m3": 960.0,
        "process_viscosity_Pa_s": 0.00028,
        "process_thermal_conductivity_W_mK": 0.68,
        "heating_htc_W_m2K": 5150.0,
        "cold_fouling_factor_m2K_W": 0.0002,
        "hot_fouling_factor_m2K_W": 0.0001,
        "design_margin": 1.0,
    })
    g = deepcopy(DEFAULT_GEOMETRY)
    g.update({"tube_count": 374, "tube_od_mm": 25.4, "tube_id_mm": 21.1,
              "tube_length_m": 3.0, "tube_passes": 1, "auto_bundle_geometry": False})
    return p, g


def test_forced_circulation_example_duty_and_mixed_lmtd():
    p, g = _forced_circ_example_inputs()
    thermal = calculate_thermal_basis(p)
    assert math.isclose(thermal["sensible_duty_W"], 836_000, rel_tol=1e-9)
    assert math.isclose(thermal["latent_duty_W"], 2_260_000, rel_tol=1e-9)
    result = calculate("Rating", "Forced Circulation Evaporator", p, g)
    assert result["status"] == "PRELIMINARY RESULT"
    assert math.isclose(result["thermal"]["raw_LMTD_K"], 20.0 / math.log(2.0), rel_tol=1e-4)
    assert "mixed sensible/latent" in result["thermal"]["LMTD_method"]


def test_equipment_selection_example_a_prefers_horizontal_thermosyphon():
    p = deepcopy(DEFAULT_PROCESS_INPUTS)
    p.update({
        "mass_flow_kg_s": 15.0, "inlet_temperature_C": 92.5,
        "boiling_temperature_C": 92.5, "latent_heat_kJ_kg": 345.0,
        "target_vapor_fraction": 0.25, "hot_in_temperature_C": 145.0,
        "hot_out_temperature_C": 130.0, "process_density_kg_m3": 565.0,
        "process_viscosity_Pa_s": 0.00021, "cold_fouling_factor_m2K_W": 0.0001,
        "boiling_range_C": 6.5, "process_pressure_bar_abs": 3.5,
        "critical_pressure_bar_abs": 0.0, "vertical_headroom_m": 3.2,
        "static_elevation_m": 1.8, "estimated_natural_loop_dp_kPa": 6.2,
        "allowable_process_dp_kPa": 35.0, "pump_permitted": False,
    })
    prep = preprocess_selection_inputs(p)
    assert math.isclose(prep["total_duty_kW"], 1293.75, rel_tol=1e-9)
    assert math.isclose(prep["available_static_head_kPa"], 565.0 * 9.81 * 1.8 / 1000, rel_tol=1e-9)
    ranked = recommend_equipment(p)
    assert ranked[0]["exchanger"] == "Horizontal Thermosyphon Reboiler"


def test_equipment_selection_example_b_prefers_kettle_and_warns_ratio_conflict():
    p = deepcopy(DEFAULT_PROCESS_INPUTS)
    p.update({"mass_flow_kg_s": 8.5, "inlet_temperature_C": 30.0,
              "boiling_temperature_C": 45.8, "cp_kJ_kgK": 4.184,
              "latent_heat_kJ_kg": 2390.0, "target_vapor_fraction": 0.25,
              "hot_in_temperature_C": 119.6, "hot_out_temperature_C": 119.6,
              "process_pressure_bar_abs": 0.10, "cold_fouling_factor_m2K_W": 0.00015,
              "boiling_range_C": 1.2, "process_density_kg_m3": 990.0,
              "static_elevation_m": 0.8})
    prep = preprocess_selection_inputs(p)
    assert math.isclose(prep["sensible_duty_kW"], 561.91, rel_tol=1e-5)
    assert math.isclose(prep["total_duty_kW"], 5640.66, rel_tol=1e-5)
    ranked = recommend_equipment(p)
    assert ranked[0]["exchanger"] == "Kettle Reboiler"
    assert any("outside the justification deck" in line for line in recommend_equipment.last_trace)


def test_all_equipment_routes_return_equipment_specific_metrics():
    for exchanger in EXCHANGERS:
        p, g = deepcopy(DEFAULT_PROCESS_INPUTS), deepcopy(DEFAULT_GEOMETRY)
        sizing = calculate("Sizing", exchanger, p, g)
        rating = calculate("Rating", exchanger, p, g)
        assert sizing["status"] == "PRELIMINARY RESULT", (exchanger, sizing)
        assert rating["status"] == "PRELIMINARY RESULT", (exchanger, rating)
        assert sizing["engineering_calculations"], exchanger
        assert rating["engineering_calculations"], exchanger
        assert "overall_U_W_m2K_calculated" in sizing["engineering_calculations"]


def test_independent_vaporization_rate_override_keeps_exit_quality_separate():
    p = deepcopy(DEFAULT_PROCESS_INPUTS)
    p.update({
        "mass_flow_kg_s": 1.0,
        "vaporization_rate_kg_s": 1.0,
        "target_vapor_fraction": 0.105,
        "inlet_temperature_C": 95.0,
        "boiling_temperature_C": 100.0,
        "cp_kJ_kgK": 4.2,
        "latent_heat_kJ_kg": 2257.0,
    })
    thermal = calculate_thermal_basis(p)
    assert math.isclose(thermal["vaporization_rate_kg_s_used"], 1.0, rel_tol=1e-12)
    assert math.isclose(thermal["sensible_duty_W"], 21_000.0, rel_tol=1e-12)
    assert math.isclose(thermal["latent_duty_W"], 2_257_000.0, rel_tol=1e-12)
    assert math.isclose(thermal["required_duty_W"], 2_278_000.0, rel_tol=1e-12)


def test_horizontal_thermosyphon_uses_source_static_head_screen_not_vertical_tube_head():
    p = deepcopy(DEFAULT_PROCESS_INPUTS)
    p.update({"mass_flow_kg_s": 15.0, "inlet_temperature_C": 92.5,
              "boiling_temperature_C": 92.5, "latent_heat_kJ_kg": 345.0,
              "target_vapor_fraction": 0.25, "hot_in_temperature_C": 145.0,
              "hot_out_temperature_C": 130.0, "process_density_kg_m3": 565.0,
              "process_vapor_density_kg_m3": 14.5, "process_surface_tension_N_m": 0.009,
              "process_viscosity_Pa_s": 0.00021, "cold_fouling_factor_m2K_W": 0.0001,
              "static_elevation_m": 1.8, "estimated_natural_loop_dp_kPa": 6.2,
              "allowable_process_dp_kPa": 35.0})
    g = deepcopy(DEFAULT_GEOMETRY)
    g.update({"tube_length_m": 6.0, "static_elevation_m": 1.8})
    result = calculate("Rating", "Horizontal Thermosyphon Reboiler", p, g)
    metrics = result["engineering_calculations"]
    assert metrics["natural_loop_balance_pass"] is True
    assert metrics["two_phase_gravity_drop_kPa"] == 0.0
    assert "source static-head/allowable-ΔP screen" in metrics["natural_loop_balance_status"]


def test_vertical_thermosyphon_zivi_example_discrepancy_is_reported():
    p = deepcopy(DEFAULT_PROCESS_INPUTS)
    p.update({"mass_flow_kg_s": 1.0, "vaporization_rate_kg_s": 1.0,
              "target_vapor_fraction": 0.105, "inlet_temperature_C": 95.0,
              "boiling_temperature_C": 100.0, "cp_kJ_kgK": 4.2,
              "latent_heat_kJ_kg": 2257.0, "process_density_kg_m3": 958.0,
              "process_vapor_density_kg_m3": 0.598, "process_surface_tension_N_m": 0.059,
              "static_elevation_m": 1.5, "estimated_natural_loop_dp_kPa": 9.8,
              "process_boiling_htc_W_m2K": 3900.0})
    g = deepcopy(DEFAULT_GEOMETRY)
    g.update({"tube_count": 310, "tube_od_mm": 25.4, "tube_id_mm": 21.1,
              "tube_length_m": 2.5, "static_elevation_m": 1.5})
    result = calculate("Rating", "Vertical Thermosyphon Reboiler", p, g)
    metrics = result["engineering_calculations"]
    assert metrics["Zivi_void_fraction_alpha"] > 0.90
    assert any("Source-example consistency warning" in warning for warning in result["warnings"])
