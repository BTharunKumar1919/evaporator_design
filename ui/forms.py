"""Reusable Streamlit input forms. Values are returned as plain dictionaries."""
from __future__ import annotations
import streamlit as st
from core.models import DEFAULT_PROCESS_INPUTS, DEFAULT_GEOMETRY


def process_input_fields(prefix: str = "p", include_preferences: bool = False) -> dict:
    d = DEFAULT_PROCESS_INPUTS
    st.subheader("Process and thermal requirements")
    c1, c2, c3 = st.columns(3)
    with c1:
        mass_flow = st.number_input("Process feed mass flow (kg/s)", min_value=0.001, value=float(d["mass_flow_kg_s"]), step=0.1, format="%.4f", key=f"{prefix}_mass_flow")
        inlet_temp = st.number_input("Feed inlet temperature (°C)", min_value=-100.0, max_value=1500.0, value=float(d["inlet_temperature_C"]), step=5.0, key=f"{prefix}_tin")
        boiling_temp = st.number_input("Process boiling temperature (°C)", min_value=-100.0, max_value=1500.0, value=float(d["boiling_temperature_C"]), step=5.0, key=f"{prefix}_tboil")
        cp = st.number_input("Liquid specific heat (kJ/kg·K)", min_value=0.001, value=float(d["cp_kJ_kgK"]), step=0.1, format="%.4f", key=f"{prefix}_cp")
    with c2:
        hfg = st.number_input("Latent heat (kJ/kg)", min_value=0.001, value=float(d["latent_heat_kJ_kg"]), step=50.0, key=f"{prefix}_hfg")
        x = st.slider("Target exit vapor mass fraction, xe", min_value=0.0, max_value=0.95, value=float(d["target_vapor_fraction"]), step=0.05, key=f"{prefix}_x", help="Used as vapor generation rate / feed rate for the preliminary selection calculation.")
        hot_in = st.number_input("Heating-medium inlet temperature (°C)", min_value=-100.0, max_value=2000.0, value=float(d["hot_in_temperature_C"]), step=5.0, key=f"{prefix}_hotin")
        hot_out = st.number_input("Heating-medium outlet temperature (°C)", min_value=-100.0, max_value=2000.0, value=float(d["hot_out_temperature_C"]), step=5.0, key=f"{prefix}_hotout")
    with c3:
        u = st.number_input("Assumed overall U (W/m²·K)", min_value=1.0, value=float(d["overall_U_W_m2K"]), step=100.0, key=f"{prefix}_u")
        f = st.number_input("LMTD correction factor F", min_value=0.1, max_value=1.5, value=float(d["LMTD_correction_factor"]), step=0.05, key=f"{prefix}_f")
        margin = st.number_input("Design margin (× duty)", min_value=1.0, max_value=2.5, value=float(d["design_margin"]), step=0.05, key=f"{prefix}_margin")
        allow_dp = st.number_input("Allowable process-side ΔP (kPa)", min_value=0.1, value=float(d["allowable_process_dp_kPa"]), step=10.0, key=f"{prefix}_allowdp")

    with st.expander("Fluid properties and heating-side pressure-drop inputs", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            rho = st.number_input("Process liquid density (kg/m³)", min_value=0.1, value=float(d["process_density_kg_m3"]), step=50.0, key=f"{prefix}_rho")
            mu = st.number_input("Process viscosity (Pa·s)", min_value=1e-7, value=float(d["process_viscosity_Pa_s"]), format="%.6f", key=f"{prefix}_mu")
        with c2:
            hot_mdot = st.number_input("Heating-medium mass flow (kg/s)", min_value=0.001, value=float(d["hot_mass_flow_kg_s"]), step=0.1, key=f"{prefix}_hotmdot")
            hot_rho = st.number_input("Heating-medium density (kg/m³)", min_value=0.1, value=float(d["hot_density_kg_m3"]), step=50.0, key=f"{prefix}_hotrho")
            hot_mu = st.number_input("Heating-medium viscosity (Pa·s)", min_value=1e-7, value=float(d["hot_viscosity_Pa_s"]), format="%.6f", key=f"{prefix}_hotmu")
        with c3:
            hot_dh = st.number_input("Heating-side equivalent hydraulic diameter (m)", min_value=0.001, value=float(d["hot_hydraulic_diameter_m"]), step=0.005, format="%.4f", key=f"{prefix}_hotdh")
            hot_area = st.number_input("Heating-side equivalent flow area (m²)", min_value=0.0001, value=float(d["hot_flow_area_m2"]), step=0.01, format="%.4f", key=f"{prefix}_hotarea")
            hot_length = st.number_input("Heating-side equivalent flow length (m)", min_value=0.01, value=float(d["hot_flow_length_m"]), step=0.5, key=f"{prefix}_hotlength")
            allow_hot_dp = st.number_input("Allowable heating-side ΔP (kPa)", min_value=0.1, value=float(d["allowable_hot_dp_kPa"]), step=10.0, key=f"{prefix}_allowhotdp")

    p = {
        "mass_flow_kg_s": mass_flow, "inlet_temperature_C": inlet_temp,
        "boiling_temperature_C": boiling_temp, "cp_kJ_kgK": cp,
        "latent_heat_kJ_kg": hfg, "target_vapor_fraction": x,
        "hot_in_temperature_C": hot_in, "hot_out_temperature_C": hot_out,
        "overall_U_W_m2K": u, "LMTD_correction_factor": f,
        "design_margin": margin, "process_density_kg_m3": rho,
        "process_viscosity_Pa_s": mu, "allowable_process_dp_kPa": allow_dp,
        "hot_mass_flow_kg_s": hot_mdot, "hot_density_kg_m3": hot_rho,
        "hot_viscosity_Pa_s": hot_mu, "hot_hydraulic_diameter_m": hot_dh,
        "hot_flow_area_m2": hot_area, "hot_flow_length_m": hot_length,
        "allowable_hot_dp_kPa": allow_hot_dp,
    }

    with st.expander("Equipment-selection inputs from the supplied algorithm", expanded=include_preferences):
        st.caption("These fields feed the priority gates. Thresholds are taken from the uploaded algorithm document; confirm them with your instructor before treating them as design rules.")
        a, b, c = st.columns(3)
        with a:
            p_pressure = st.number_input("Process pressure, absolute (bar)", min_value=0.001, value=float(d["process_pressure_bar_abs"]), step=0.1, key=f"{prefix}_pc")
            h_pressure = st.number_input("Heating-medium pressure, absolute (bar)", min_value=0.001, value=float(d["heating_pressure_bar_abs"]), step=0.5, key=f"{prefix}_ph")
            pcrit = st.number_input("Process-fluid critical pressure (bar abs; 0 if unknown)", min_value=0.0, value=float(d["critical_pressure_bar_abs"]), step=1.0, key=f"{prefix}_pcrit")
            br = st.number_input("Boiling range, Tdew − Tbubble (°C)", min_value=0.0, value=float(d["boiling_range_C"]), step=0.5, key=f"{prefix}_br")
            rf_c = st.number_input("Process-side fouling factor (m²·K/W)", min_value=0.0, value=float(d["cold_fouling_factor_m2K_W"]), format="%.6f", key=f"{prefix}_rfc")
            rf_h = st.number_input("Heating-side fouling factor (m²·K/W)", min_value=0.0, value=float(d["hot_fouling_factor_m2K_W"]), format="%.6f", key=f"{prefix}_rfh")
        with b:
            headroom = st.number_input("Available vertical headroom (m)", min_value=0.0, value=float(d["vertical_headroom_m"]), step=0.5, key=f"{prefix}_headroom")
            floor_length = st.number_input("Available horizontal floor length (m)", min_value=0.0, value=float(d["horizontal_floor_space_m"]), step=0.5, key=f"{prefix}_floorlength")
            floor_restricted = st.checkbox("Horizontal floor space is restricted", value=bool(d["floor_space_restricted"]), key=f"{prefix}_floorrestricted")
            static_elev = st.number_input("Static liquid elevation / sump head (m)", min_value=0.0, value=float(d["static_elevation_m"]), step=0.2, key=f"{prefix}_static")
            pump_allowed = st.checkbox("Pump permitted", value=bool(d["pump_permitted"]), key=f"{prefix}_pump")
            loop_dp_txt = st.text_input("Estimated natural-loop friction + acceleration ΔP (kPa; blank = unknown)", value="", key=f"{prefix}_loopdp", help="Enter a value only if you have an estimate from the course algorithm. The program will not invent this loss.")
        with c:
            heat_sensitive = st.checkbox("Heat-sensitive product", value=bool(d["heat_sensitive"]), key=f"{prefix}_heatsens")
            unstable = st.checkbox("Thermally unstable product", value=bool(d["thermally_unstable"]), key=f"{prefix}_unstable")
            slurry = st.checkbox("Crystallizing / slurry service", value=bool(d["crystallizing_slurry"]), key=f"{prefix}_slurry")
            fouling_solids = st.checkbox("Fouling or suspended solids concern", value=bool(d["fouling_or_solids"]), key=f"{prefix}_fouling")
            high_flux = st.checkbox("High heat-flux duty", value=bool(d["high_heat_flux"]), key=f"{prefix}_highflux")
            heating_corrosive = st.checkbox("Heating medium is severely corrosive", value=bool(d["heating_medium_corrosive"]), key=f"{prefix}_corrosive")
            corrosive_process = st.checkbox("Process fluid is corrosive / toxic", value=bool(d["corrosive_toxic_process"]), key=f"{prefix}_processcorrosive")
            foaming = st.checkbox("Foaming tendency", value=bool(d["foaming"]), key=f"{prefix}_foaming")

    p.update({
        "process_pressure_bar_abs": p_pressure, "heating_pressure_bar_abs": h_pressure,
        "critical_pressure_bar_abs": pcrit, "boiling_range_C": br,
        "cold_fouling_factor_m2K_W": rf_c, "hot_fouling_factor_m2K_W": rf_h,
        "vertical_headroom_m": headroom, "horizontal_floor_space_m": floor_length,
        "floor_space_restricted": floor_restricted, "static_elevation_m": static_elev,
        "pump_permitted": pump_allowed,
        "estimated_natural_loop_dp_kPa": loop_dp_txt.strip() or None,
        "heat_sensitive": heat_sensitive, "thermally_unstable": unstable,
        "crystallizing_slurry": slurry, "fouling_or_solids": fouling_solids,
        "high_heat_flux": high_flux, "heating_medium_corrosive": heating_corrosive,
        "corrosive_toxic_process": corrosive_process, "foaming": foaming,
        "natural_circulation_preferred": not pump_allowed,
    })
    return p


def geometry_input_fields(prefix: str = "g", rating: bool = False) -> dict:
    d = DEFAULT_GEOMETRY
    st.subheader("Exchanger geometry")
    if rating:
        tube_count = st.number_input("Existing tube count", min_value=1, max_value=100000, value=int(d["tube_count"]), step=10, key=f"{prefix}_count")
    else:
        tube_count = int(d["tube_count"])
        st.caption("Tube count is calculated from required area. The other dimensions below define the preliminary tube size.")
    c1, c2, c3 = st.columns(3)
    with c1:
        od = st.number_input("Tube outside diameter (mm)", min_value=1.0, value=float(d["tube_od_mm"]), step=1.0, key=f"{prefix}_od")
        id_ = st.number_input("Tube inside diameter (mm)", min_value=0.5, value=float(d["tube_id_mm"]), step=1.0, key=f"{prefix}_id")
        length = st.number_input("Tube length (m)", min_value=0.1, value=float(d["tube_length_m"]), step=0.5, key=f"{prefix}_length")
    with c2:
        passes = st.number_input("Tube passes", min_value=1, max_value=16, value=int(d["tube_passes"]), step=1, key=f"{prefix}_passes")
        shell = st.number_input("Shell diameter (m)", min_value=0.05, value=float(d["shell_diameter_m"]), step=0.05, key=f"{prefix}_shell")
        bundle = st.number_input("Bundle diameter (m)", min_value=0.05, value=float(d["bundle_diameter_m"]), step=0.05, key=f"{prefix}_bundle")
    with c3:
        baffle = st.number_input("Baffle spacing (m; where relevant)", min_value=0.01, value=float(d["baffle_spacing_m"]), step=0.05, key=f"{prefix}_baffle")
        level = st.number_input("Liquid level (m; where relevant)", min_value=0.01, value=float(d["liquid_level_m"]), step=0.05, key=f"{prefix}_level")
        circulation = st.number_input("Circulation ratio (where relevant)", min_value=0.1, value=float(d["circulation_ratio"]), step=0.5, key=f"{prefix}_circ")
        elevation = st.number_input("Static elevation (m; where relevant)", min_value=0.0, value=float(d["static_elevation_m"]), step=0.5, key=f"{prefix}_elev")
    return {"tube_count": int(tube_count), "tube_od_mm": od, "tube_id_mm": id_, "tube_length_m": length,
            "tube_passes": int(passes), "shell_diameter_m": shell, "bundle_diameter_m": bundle,
            "baffle_spacing_m": baffle, "liquid_level_m": level, "circulation_ratio": circulation,
            "static_elevation_m": elevation}
