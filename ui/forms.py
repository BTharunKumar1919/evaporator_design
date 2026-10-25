"""Reusable Streamlit input forms for process, property and geometry data."""
from __future__ import annotations
import streamlit as st
from core.models import DEFAULT_PROCESS_INPUTS, DEFAULT_GEOMETRY


def process_input_fields(prefix: str = "p", include_preferences: bool = False) -> dict:
    d = DEFAULT_PROCESS_INPUTS
    st.subheader("Process and thermal requirements")
    c1, c2, c3 = st.columns(3)
    with c1:
        mass_flow = st.number_input("Process feed mass flow (kg/s)", min_value=0.001, value=float(d["mass_flow_kg_s"]), step=0.1, format="%.4f", key=f"{prefix}_mass_flow")
        vapor_rate = st.number_input("Vaporization rate override (kg/s; 0 derives feed × xe)", min_value=0.0, value=float(d["vaporization_rate_kg_s"]), step=0.1, format="%.4f", key=f"{prefix}_vapor_rate", help="Use a positive value when a worked example specifies vapor generation independently from exit vapor quality. This controls latent duty; xe remains the separate quality input used by selection/safety gates.")
        inlet_temp = st.number_input("Feed inlet temperature (°C)", min_value=-100.0, max_value=1500.0, value=float(d["inlet_temperature_C"]), step=5.0, key=f"{prefix}_tin")
        boiling_temp = st.number_input("Process boiling temperature (°C)", min_value=-100.0, max_value=1500.0, value=float(d["boiling_temperature_C"]), step=5.0, key=f"{prefix}_tboil")
        cp = st.number_input("Liquid specific heat (kJ/kg·K)", min_value=0.001, value=float(d["cp_kJ_kgK"]), step=0.1, format="%.4f", key=f"{prefix}_cp")
    with c2:
        hfg = st.number_input("Process latent heat (kJ/kg)", min_value=0.001, value=float(d["latent_heat_kJ_kg"]), step=50.0, key=f"{prefix}_hfg")
        x = st.slider("Target exit vapor mass fraction, xe", min_value=0.0, max_value=0.95, value=float(d["target_vapor_fraction"]), step=0.05, key=f"{prefix}_x", help="This is the exit vapor mass fraction used by selection/quality checks. Latent duty uses feed flow × xe unless a positive vaporization-rate override is entered.")
        hot_in = st.number_input("Heating-medium inlet temperature (°C)", min_value=-100.0, max_value=2000.0, value=float(d["hot_in_temperature_C"]), step=5.0, key=f"{prefix}_hotin")
        hot_out = st.number_input("Heating-medium outlet temperature (°C)", min_value=-100.0, max_value=2000.0, value=float(d["hot_out_temperature_C"]), step=5.0, key=f"{prefix}_hotout")
    with c3:
        u = st.number_input("Fallback overall U (W/m²·K)", min_value=1.0, value=float(d["overall_U_W_m2K"]), step=100.0, key=f"{prefix}_u", help="Used only if an equipment-specific coefficient cannot be calculated from the available inputs.")
        f = st.number_input("LMTD correction factor F", min_value=0.1, max_value=1.5, value=float(d["LMTD_correction_factor"]), step=0.05, key=f"{prefix}_f")
        margin = st.number_input("Additional duty multiplier (usually 1.00; area gate adds 10–20% margin)", min_value=1.0, max_value=2.5, value=float(d["design_margin"]), step=0.05, key=f"{prefix}_margin")
        allow_dp = st.number_input("Allowable process-side ΔP (kPa)", min_value=0.1, value=float(d["allowable_process_dp_kPa"]), step=10.0, key=f"{prefix}_allowdp")

    with st.expander("Thermophysical properties, coefficients and hydraulic limits", expanded=False):
        a, b, c = st.columns(3)
        with a:
            rho = st.number_input("Process liquid density (kg/m³)", min_value=0.1, value=float(d["process_density_kg_m3"]), step=25.0, key=f"{prefix}_rho")
            mu = st.number_input("Process liquid viscosity (Pa·s)", min_value=1e-7, value=float(d["process_viscosity_Pa_s"]), format="%.7f", key=f"{prefix}_mu")
            k = st.number_input("Process thermal conductivity (W/m·K)", min_value=0.001, value=float(d["process_thermal_conductivity_W_mK"]), step=0.05, key=f"{prefix}_pk")
            sigma = st.number_input("Process surface tension (N/m)", min_value=0.0001, value=float(d["process_surface_tension_N_m"]), format="%.5f", key=f"{prefix}_sigma")
            rho_v = st.number_input("Process vapor density (kg/m³)", min_value=0.0001, value=float(d["process_vapor_density_kg_m3"]), step=0.5, key=f"{prefix}_rhov")
        with b:
            hot_mdot = st.number_input("Heating-medium mass flow (kg/s)", min_value=0.001, value=float(d["hot_mass_flow_kg_s"]), step=0.1, key=f"{prefix}_hotmdot")
            hot_rho = st.number_input("Heating-medium density (kg/m³)", min_value=0.1, value=float(d["hot_density_kg_m3"]), step=25.0, key=f"{prefix}_hotrho")
            hot_mu = st.number_input("Heating-medium viscosity (Pa·s)", min_value=1e-7, value=float(d["hot_viscosity_Pa_s"]), format="%.7f", key=f"{prefix}_hotmu")
            hot_dh = st.number_input("Heating-side equivalent hydraulic diameter (m)", min_value=0.001, value=float(d["hot_hydraulic_diameter_m"]), step=0.005, format="%.4f", key=f"{prefix}_hotdh")
            hot_area = st.number_input("Heating-side equivalent flow area (m²)", min_value=0.0001, value=float(d["hot_flow_area_m2"]), step=0.01, format="%.4f", key=f"{prefix}_hotarea")
            hot_length = st.number_input("Heating-side equivalent flow length (m)", min_value=0.01, value=float(d["hot_flow_length_m"]), step=0.5, key=f"{prefix}_hotlength")
        with c:
            hot_htc = st.number_input("Heating-side HTC, assumed/verified (W/m²·K)", min_value=1.0, value=float(d["heating_htc_W_m2K"]), step=250.0, key=f"{prefix}_hothtc", help="For condensing steam, the source examples generally assume a coefficient or report an iterative result; this input is not falsely presented as a full wall-temperature solution.")
            process_boiling_htc = st.number_input("Chen/effective process boiling HTC (W/m²·K)", min_value=1.0, value=float(d["process_boiling_htc_W_m2K"]), step=250.0, key=f"{prefix}_procboilhtc")
            pool_boiling_htc = st.number_input("Baseline pool-boiling HTC before bundle factor (W/m²·K)", min_value=1.0, value=float(d["pool_boiling_htc_W_m2K"]), step=250.0, key=f"{prefix}_poolhtc", help="Provide the baseline h_nb from your approved correlation. The supplied Mostinski equation/example has a unit/arithmetic mismatch, so it is not silently automated.")
            hnc = st.number_input("Natural-convection boiling HTC add-on (W/m²·K)", min_value=0.0, value=float(d["natural_convection_htc_W_m2K"]), step=50.0, key=f"{prefix}_hnc")
            wall_k = st.number_input("Tube wall conductivity (W/m·K)", min_value=0.1, value=float(d["tube_wall_conductivity_W_mK"]), step=1.0, key=f"{prefix}_wallk")
            allow_hot_dp = st.number_input("Allowable heating-side ΔP (kPa)", min_value=0.1, value=float(d["allowable_hot_dp_kPa"]), step=10.0, key=f"{prefix}_allowhotdp")
            min_wet = st.number_input("Minimum falling-film wetting rate Γmin (kg/m·s)", min_value=0.001, value=float(d["minimum_film_wetting_rate_kg_m_s"]), step=0.01, key=f"{prefix}_minwet")
            sb_k = st.number_input("Souders–Brown K (m/s)", min_value=0.001, value=float(d["souders_brown_K_m_s"]), step=0.01, key=f"{prefix}_sbk")
            wallis_limit = st.number_input("Wallis flooding screening limit", min_value=0.1, value=float(d["wallis_flooding_limit"]), step=0.025, key=f"{prefix}_wallis")
            pump_velocity = st.number_input("Forced-circulation target velocity (m/s)", min_value=0.1, value=float(d["forced_circulation_velocity_m_s"]), step=0.25, key=f"{prefix}_targetvel")
            pump_flow = st.number_input("Existing pump flow rate (m³/s; Rating mode)", min_value=0.0001, value=float(d["pump_flow_rate_m3_s"]), step=0.01, format="%.4f", key=f"{prefix}_pumpflow")
            pump_eff = st.number_input("Pump efficiency for power estimate", min_value=0.1, max_value=1.0, value=float(d["pump_efficiency"]), step=0.05, key=f"{prefix}_pumpeff")

    p = {
        "mass_flow_kg_s": mass_flow, "vaporization_rate_kg_s": vapor_rate,
        "inlet_temperature_C": inlet_temp, "boiling_temperature_C": boiling_temp, "cp_kJ_kgK": cp,
        "latent_heat_kJ_kg": hfg, "target_vapor_fraction": x,
        "hot_in_temperature_C": hot_in, "hot_out_temperature_C": hot_out,
        "overall_U_W_m2K": u, "LMTD_correction_factor": f,
        "design_margin": margin, "process_density_kg_m3": rho,
        "process_viscosity_Pa_s": mu, "process_thermal_conductivity_W_mK": k,
        "process_surface_tension_N_m": sigma, "process_vapor_density_kg_m3": rho_v,
        "heating_htc_W_m2K": hot_htc, "process_boiling_htc_W_m2K": process_boiling_htc,
        "pool_boiling_htc_W_m2K": pool_boiling_htc, "natural_convection_htc_W_m2K": hnc,
        "tube_wall_conductivity_W_mK": wall_k, "minimum_film_wetting_rate_kg_m_s": min_wet,
        "souders_brown_K_m_s": sb_k, "wallis_flooding_limit": wallis_limit,
        "forced_circulation_velocity_m_s": pump_velocity, "pump_flow_rate_m3_s": pump_flow,
        "pump_efficiency": pump_eff, "allowable_process_dp_kPa": allow_dp,
        "hot_mass_flow_kg_s": hot_mdot, "hot_density_kg_m3": hot_rho,
        "hot_viscosity_Pa_s": hot_mu, "hot_hydraulic_diameter_m": hot_dh,
        "hot_flow_area_m2": hot_area, "hot_flow_length_m": hot_length,
        "allowable_hot_dp_kPa": allow_hot_dp,
    }

    with st.expander("Pressures, material and equipment-selection inputs", expanded=include_preferences):
        a, b, c = st.columns(3)
        with a:
            p_pressure = st.number_input("Process pressure, absolute (bar)", min_value=0.001, value=float(d["process_pressure_bar_abs"]), step=0.1, key=f"{prefix}_pc")
            h_pressure = st.number_input("Heating-medium pressure, absolute (bar)", min_value=0.001, value=float(d["heating_pressure_bar_abs"]), step=0.5, key=f"{prefix}_ph")
            pcrit = st.number_input("Process critical pressure (bar abs; 0 if unknown)", min_value=0.0, value=float(d["critical_pressure_bar_abs"]), step=1.0, key=f"{prefix}_pcrit")
            br = st.number_input("Boiling range, Tdew − Tbubble (°C)", min_value=0.0, value=float(d["boiling_range_C"]), step=0.5, key=f"{prefix}_br")
            rf_c = st.number_input("Process-side fouling factor (m²·K/W)", min_value=0.0, value=float(d["cold_fouling_factor_m2K_W"]), format="%.6f", key=f"{prefix}_rfc")
            rf_h = st.number_input("Heating-side fouling factor (m²·K/W)", min_value=0.0, value=float(d["hot_fouling_factor_m2K_W"]), format="%.6f", key=f"{prefix}_rfh")
        with b:
            headroom = st.number_input("Available vertical headroom (m)", min_value=0.0, value=float(d["vertical_headroom_m"]), step=0.5, key=f"{prefix}_headroom")
            floor_length = st.number_input("Available horizontal floor length (m)", min_value=0.0, value=float(d["horizontal_floor_space_m"]), step=0.5, key=f"{prefix}_floorlength")
            floor_restricted = st.checkbox("Horizontal floor space is restricted", value=bool(d["floor_space_restricted"]), key=f"{prefix}_floorrestricted")
            static_elev = st.number_input("Static liquid elevation / sump head (m)", min_value=0.0, value=float(d["static_elevation_m"]), step=0.2, key=f"{prefix}_static")
            pump_allowed = st.checkbox("Pump permitted", value=bool(d["pump_permitted"]), key=f"{prefix}_pump")
            loop_dp_txt = st.text_input("Estimated natural-loop friction + acceleration ΔP (kPa; blank = unknown)", value="", key=f"{prefix}_loopdp", help="Enter only a value you have estimated from the course method. The program does not invent a two-phase loop loss.")
        with c:
            design_pressure = st.number_input("Mechanical design pressure (MPa; 0 disables thickness screen)", min_value=0.0, value=float(d["design_pressure_MPa"]), step=0.1, key=f"{prefix}_pdesign")
            stress = st.number_input("Verified material allowable stress (MPa)", min_value=1.0, value=float(d["allowable_stress_MPa"]), step=10.0, key=f"{prefix}_stress")
            joint = st.number_input("Weld joint efficiency E (0–1)", min_value=0.1, max_value=1.0, value=float(d["joint_efficiency"]), step=0.05, key=f"{prefix}_joint")
            ca = st.number_input("Corrosion allowance (mm)", min_value=0.0, value=float(d["corrosion_allowance_mm"]), step=0.5, key=f"{prefix}_ca")
            heat_sensitive = st.checkbox("Heat-sensitive product", value=bool(d["heat_sensitive"]), key=f"{prefix}_heatsens")
            unstable = st.checkbox("Thermally unstable product", value=bool(d["thermally_unstable"]), key=f"{prefix}_unstable")
            slurry = st.checkbox("Crystallizing / slurry service", value=bool(d["crystallizing_slurry"]), key=f"{prefix}_slurry")
            fouling_solids = st.checkbox("Fouling or suspended-solids concern", value=bool(d["fouling_or_solids"]), key=f"{prefix}_fouling")
            high_flux = st.checkbox("High heat-flux duty", value=bool(d["high_heat_flux"]), key=f"{prefix}_highflux")
            heating_corrosive = st.checkbox("Heating medium severely corrosive", value=bool(d["heating_medium_corrosive"]), key=f"{prefix}_corrosive")
            corrosive_process = st.checkbox("Process fluid corrosive / toxic", value=bool(d["corrosive_toxic_process"]), key=f"{prefix}_processcorrosive")
            foaming = st.checkbox("Foaming tendency", value=bool(d["foaming"]), key=f"{prefix}_foaming")

    p.update({
        "process_pressure_bar_abs": p_pressure, "heating_pressure_bar_abs": h_pressure,
        "critical_pressure_bar_abs": pcrit, "boiling_range_C": br,
        "cold_fouling_factor_m2K_W": rf_c, "hot_fouling_factor_m2K_W": rf_h,
        "vertical_headroom_m": headroom, "horizontal_floor_space_m": floor_length,
        "floor_space_restricted": floor_restricted, "static_elevation_m": static_elev,
        "pump_permitted": pump_allowed, "estimated_natural_loop_dp_kPa": loop_dp_txt.strip() or None,
        "design_pressure_MPa": design_pressure, "allowable_stress_MPa": stress,
        "joint_efficiency": joint, "corrosion_allowance_mm": ca,
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
        st.caption("Sizing mode iterates tube count against the equipment-specific 10–20% area gate (10–25% for falling film).")
    c1, c2, c3 = st.columns(3)
    with c1:
        od = st.number_input("Tube outside diameter (mm)", min_value=1.0, value=float(d["tube_od_mm"]), step=1.0, key=f"{prefix}_od")
        id_ = st.number_input("Tube inside diameter (mm)", min_value=0.5, value=float(d["tube_id_mm"]), step=1.0, key=f"{prefix}_id")
        length = st.number_input("Tube length (m)", min_value=0.1, value=float(d["tube_length_m"]), step=0.5, key=f"{prefix}_length")
        pitch_ratio = st.number_input("Tube pitch / OD", min_value=1.05, max_value=2.5, value=float(d["tube_pitch_ratio"]), step=0.05, key=f"{prefix}_pitchratio")
        layout = st.selectbox("Tube layout", ["Square", "Triangular / staggered"], index=0 if d["tube_layout"] == "Square" else 1, key=f"{prefix}_layout")
    with c2:
        passes = st.number_input("Tube passes", min_value=1, max_value=16, value=int(d["tube_passes"]), step=1, key=f"{prefix}_passes")
        shell = st.number_input("Shell diameter (m)", min_value=0.05, value=float(d["shell_diameter_m"]), step=0.05, key=f"{prefix}_shell")
        bundle = st.number_input("Bundle diameter (m)", min_value=0.05, value=float(d["bundle_diameter_m"]), step=0.05, key=f"{prefix}_bundle")
        if not rating:
            auto_bundle = st.checkbox("Estimate bundle/shell dimensions during sizing", value=True, key=f"{prefix}_autobundle")
        else:
            auto_bundle = False
            st.caption("Rating uses the entered shell and bundle dimensions unchanged.")
    with c3:
        baffle = st.number_input("Baffle spacing (m; where relevant)", min_value=0.01, value=float(d["baffle_spacing_m"]), step=0.05, key=f"{prefix}_baffle")
        level = st.number_input("Liquid level / sump head (m)", min_value=0.0, value=float(d["liquid_level_m"]), step=0.05, key=f"{prefix}_level")
        circulation = st.number_input("Recirculation ratio (reference/input)", min_value=0.1, value=float(d["circulation_ratio"]), step=0.5, key=f"{prefix}_circ")
        elevation = st.number_input("Static elevation (m)", min_value=0.0, value=float(d["static_elevation_m"]), step=0.5, key=f"{prefix}_elev")
        weir = st.number_input("Kettle / distributor weir height (m)", min_value=0.0, value=float(d["weir_height_m"]), step=0.01, key=f"{prefix}_weir")
        holes = st.number_input("Falling-film distributor hole count", min_value=1, max_value=100000, value=int(d["distributor_hole_count"]), step=10, key=f"{prefix}_holes")
        hole_d = st.number_input("Distributor hole diameter (mm)", min_value=0.5, value=float(d["distributor_hole_diameter_mm"]), step=0.2, key=f"{prefix}_holed")
        hole_cd = st.number_input("Distributor discharge coefficient Cd", min_value=0.1, max_value=1.0, value=float(d["distributor_discharge_coefficient"]), step=0.02, key=f"{prefix}_holecd")
    return {
        "tube_count": int(tube_count), "tube_od_mm": od, "tube_id_mm": id_, "tube_length_m": length,
        "tube_passes": int(passes), "shell_diameter_m": shell, "bundle_diameter_m": bundle,
        "baffle_spacing_m": baffle, "liquid_level_m": level, "circulation_ratio": circulation,
        "static_elevation_m": elevation, "tube_pitch_ratio": pitch_ratio,
        "tube_pitch_m": 0.0, "tube_layout": layout, "auto_bundle_geometry": auto_bundle,
        "weir_height_m": weir, "distributor_hole_count": int(holes),
        "distributor_hole_diameter_mm": hole_d, "distributor_discharge_coefficient": hole_cd,
    }
