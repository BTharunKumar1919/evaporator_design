from copy import deepcopy

from core.models import DEFAULT_PROCESS_INPUTS, DEFAULT_GEOMETRY, EXCHANGERS
from core.solver import calculate
from calculations.common.thermal import calculate_thermal_basis, lmtd_for_constant_boiling_temperature
from calculations.common.hydraulics import darcy_pressure_drop_kPa


def test_thermal_basis_default_case():
    result = calculate_thermal_basis(deepcopy(DEFAULT_PROCESS_INPUTS))
    assert round(result["sensible_duty_W"]) == 229900
    assert round(result["latent_duty_W"]) == 460000
    assert round(result["required_duty_W"]) == 689900
    assert result["LMTD_K"] == 40.0


def test_all_exchangers_have_sizing_routes():
    for name in EXCHANGERS:
        result = calculate("Sizing", name, deepcopy(DEFAULT_PROCESS_INPUTS), deepcopy(DEFAULT_GEOMETRY))
        assert result["status"] == "PRELIMINARY RESULT", (name, result)
        assert result["required_area_m2"] > 0
        assert result["tube_count_required"] >= 1
        assert result["installed_area_m2"] >= result["required_area_m2"]


def test_all_exchangers_have_rating_routes():
    for name in EXCHANGERS:
        result = calculate("Rating", name, deepcopy(DEFAULT_PROCESS_INPUTS), deepcopy(DEFAULT_GEOMETRY))
        assert result["status"] == "PRELIMINARY RESULT", (name, result)
        assert result["available_area_m2"] > 0
        assert result["capacity_W"] > 0
        assert 0 <= result["achieved_vapor_fraction"] <= 1


def test_lmtd_rejects_nonpositive_approach():
    value, warnings = lmtd_for_constant_boiling_temperature(75, 90, 80)
    assert value is None
    assert warnings


def test_pressure_drop_is_nonnegative():
    result = darcy_pressure_drop_kPa(1.0, 1000.0, 0.001, 0.016, 0.02, 3.0)
    assert result["delta_p_kPa"] >= 0
    assert result["velocity_m_s"] > 0


def test_unit_conversions():
    from core.unit_conversion import mm_to_m, m_to_mm, kJ_to_J, Pa_to_kPa
    assert mm_to_m(19.0) == 0.019
    assert m_to_mm(0.019) == 19.0
    assert kJ_to_J(2.3) == 2300.0
    assert Pa_to_kPa(2500.0) == 2.5
