# Equipment-selection review and worked examples

This review compares the existing starter implementation against the uploaded `equipment selection Algorithm Justification.pdf` and `Equip allocation sample problem.pdf`.

## What changed

The previous `core/equipment_selection.py` was only a qualitative preference score: it did not calculate exit vapor fraction, recirculation ratio, heat duty, effective temperature approach, or static head. It also omitted the stated priority gates, pressure extremes, boiling range, fouling-factor thresholds, headroom, pump constraint, hydraulic-loop validation, and fluid-side allocation.

The updated implementation now:

1. Calculates `xe`, vapor rate, `R`, sensible/latent duty, `ΔTeff`, and `ΔPstatic`.
2. Applies the gates in priority order: Gate 1, then Gate 2, then Gate 3, then natural-circulation Loop A and Gate 4 only when earlier gates do not trigger.
3. Ranks candidates with a transparent score and reasons/cautions. The first-ranked item is preselected, but the user can select any listed type.
4. Shows the gate trace and estimated tube-side/shell-side allocation in the GUI.
5. Leaves natural-loop feasibility as UNKNOWN when the user does not supply an estimated frictional + acceleration pressure loss. It does not invent a two-phase pressure drop.
6. Warns about an internal inconsistency in the supplied deep-vacuum example (see below).

## Worked Problem 1 — Petrochemical hydrocarbon reboiler

Source inputs from the sample problem:

- Feed: 15 kg/s; target vapor rate: 3.75 kg/s, so `xe = 3.75/15 = 0.25`.
- `R = (1 - xe)/xe = 3.0`.
- Feed enters at its boiling temperature, 92.5 °C, so sensible duty is zero.
- Latent heat: 345 kJ/kg, so `Q = 3.75 × 345 = 1293.75 kW`.
- Heating-medium temperatures: 145 and 130 °C; mean = 137.5 °C.
- `ΔTeff = 137.5 - 92.5 = 45 °C`.
- Liquid density 565 kg/m³ and static elevation 1.8 m give `ΔPstatic = 565 × 9.81 × 1.8 / 1000 = 9.98 kPa`.
- Viscosity 0.21 cP, cold-side fouling factor 0.0001 m²·K/W, boiling range 6.5 °C, pressure 3.5 bar abs, headroom 3.2 m, pump not permitted, estimated loop loss 6.2 kPa, allowable pressure drop 35 kPa.

Gate trace:

1. Gate 1 is not triggered: viscosity < 50 cP, no slurry, fouling < 0.0004, high-heat-flux flag false.
2. Gate 2 is not triggered: not heat-sensitive and `ΔTeff = 45 °C > 8 °C`.
3. Gate 3 is not triggered: `xe = 0.25 < 0.35`, pressure is not deep vacuum, and critical pressure is not supplied (near-critical check is therefore disabled).
4. Loop A: estimated loss 6.2 kPa is less than static head 9.98 kPa and allowable ΔP 35 kPa, so the supplied estimate passes the preliminary inequality.
5. Gate 4: headroom 3.2 m < 4.5 m, so horizontal thermosyphon receives the strongest geometry preference.

Expected leading recommendation: **Horizontal Thermosyphon Reboiler**. This matches the worked problem's selected TEMA G-shell. It is still a preliminary selection; the 6.2 kPa loop loss is accepted as user-supplied example data, not calculated by this program.

## Worked Problem 2 — Aqueous chemical evaporator

Source inputs:

- Feed: 8.5 kg/s; vapor rate 2.125 kg/s, so `xe = 0.25` and `R = 3.0`.
- `Tfeed = 30 °C`, `Tsat = 45.8 °C`, `cp = 4.184 kJ/(kg·K)`, `hfg = 2390 kJ/kg`.
- Sensible duty calculated from the stated equation: `8.5 × 4.184 × (45.8 - 30) = 561.91 kW`.
- Latent duty: `2.125 × 2390 = 5078.75 kW`.
- Total using those inputs: **5640.66 kW**.
- Heating temperature 119.6 °C, so `ΔTeff = 73.8 °C`.
- Density 990 kg/m³ and static elevation 0.8 m give `ΔPstatic = 7.77 kPa`.
- Pressure 0.10 bar abs (deep vacuum), cold-side fouling 0.00015 m²·K/W, boiling range 1.2 °C.

Gate trace:

1. Gate 1 is not triggered.
2. Gate 2 is not triggered.
3. Gate 3 is triggered by deep vacuum (`0.10 <= 0.15 bar abs`). The kettle sub-gate passes because fouling <= 0.0002 and boiling range < 10 °C.
4. The Kettle Reboiler is therefore the leading recommendation, matching the supplied worked example.

### Arithmetic discrepancy in the supplied sample

The sample PDF reports sensible duty as 561.304 kW and total duty as 5640.054 kW. Substituting its printed values directly into its printed equation gives approximately 561.91 kW sensible and 5640.66 kW total (small discrepancy, likely arithmetic or transcription). The code uses the equation and input values rather than hard-coding the reported total.

### Algorithm discrepancy in the supplied documents

The justification deck says the desired recirculation ratio under vacuum is approximately 15–18 (and elsewhere gives an aqueous/vacuum range around 10–25). However, the worked deep-vacuum example uses `xe = 2.125/8.5 = 0.25`, which gives `R = 3`, and still selects a kettle. These statements conflict. The code does **not** silently force a different vapor fraction or reject the sample; it displays a warning so the team can confirm the intended criterion with the instructor.

## Important limitations retained deliberately

- The near-critical gate can only be evaluated if the process fluid's critical pressure is entered. A value of zero means unknown/disabled, not proof that the fluid is not near-critical.
- The program does not calculate two-phase friction/acceleration pressure drop for Loop A. If no estimate is entered, natural-circulation feasibility is reported as unknown.
- `ΔTeff = mean heating-medium temperature - process boiling temperature` is the approximation used in the supplied algorithm; it is not a substitute for a detailed temperature profile or boiling-point-elevation calculation.
- Side allocation is displayed as a starting recommendation. Corrosion/material selection and exchanger-specific allocation require engineering review.
- Scores are a transparent ranking layer over the priority gates, not probabilities or a certified optimization objective. The user may override the top-ranked recommendation, with cautions shown.
