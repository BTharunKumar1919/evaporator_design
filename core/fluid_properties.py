"""Fluid-property boundary for the starter project.

For the first version, properties are supplied by the user in the GUI. This
module provides one place to replace manual inputs with a validated property
package or project-approved tabulated data later. No automatic property model
is implied here.
"""
from __future__ import annotations

REQUIRED_KEYS = (
    "cp_kJ_kgK",
    "latent_heat_kJ_kg",
    "process_density_kg_m3",
    "process_viscosity_Pa_s",
)


def manual_property_record(process_inputs: dict) -> dict:
    missing = [key for key in REQUIRED_KEYS if key not in process_inputs]
    if missing:
        raise ValueError("Missing manually entered fluid properties: " + ", ".join(missing))
    return {
        "source": "user-entered input; no property-package lookup performed",
        "cp_kJ_kgK": float(process_inputs["cp_kJ_kgK"]),
        "latent_heat_kJ_kg": float(process_inputs["latent_heat_kJ_kg"]),
        "density_kg_m3": float(process_inputs["process_density_kg_m3"]),
        "viscosity_Pa_s": float(process_inputs["process_viscosity_Pa_s"]),
    }
