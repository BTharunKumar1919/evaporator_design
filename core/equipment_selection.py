"""Transparent preliminary heuristic for recommending evaporator types.

This is a starter heuristic, not a standards-backed selection model. Replace or
revise these rules after the team's flowchart is reviewed by the instructor.
"""
from __future__ import annotations

NAMES = [
    "Falling Film Evaporator",
    "Forced Circulation Evaporator",
    "Vertical Thermosyphon Reboiler",
    "Horizontal Thermosyphon Reboiler",
    "Kettle Reboiler",
]


def recommend_equipment(p: dict) -> list[dict]:
    scores = {name: 0 for name in NAMES}
    reasons = {name: [] for name in NAMES}
    if p.get("heat_sensitive", False):
        scores["Falling Film Evaporator"] += 3
        reasons["Falling Film Evaporator"].append("heat-sensitive service preference")
        scores["Kettle Reboiler"] -= 1
    if p.get("fouling_or_solids", False):
        scores["Forced Circulation Evaporator"] += 4
        reasons["Forced Circulation Evaporator"].append("fouling/solids preference; higher circulation can help manage deposition")
        scores["Falling Film Evaporator"] -= 2
        scores["Vertical Thermosyphon Reboiler"] -= 1
        scores["Horizontal Thermosyphon Reboiler"] -= 1
    if p.get("natural_circulation_preferred", True):
        for name in ["Vertical Thermosyphon Reboiler", "Horizontal Thermosyphon Reboiler"]:
            scores[name] += 2
            reasons[name].append("natural-circulation preference")
    x = float(p.get("target_vapor_fraction", 0.2))
    if x >= 0.4:
        scores["Kettle Reboiler"] += 2
        reasons["Kettle Reboiler"].append("relatively high target vapor fraction")
        scores["Forced Circulation Evaporator"] += 1
        reasons["Forced Circulation Evaporator"].append("relatively high target vapor fraction")
    else:
        scores["Falling Film Evaporator"] += 1
        reasons["Falling Film Evaporator"].append("modest target vapor fraction")
    ranked = sorted(NAMES, key=lambda name: scores[name], reverse=True)
    return [
        {"exchanger": name, "score": scores[name], "reasons": reasons[name] or ["No preference rule matched; retained as a candidate."],
         "rank": i + 1}
        for i, name in enumerate(ranked)
    ]
