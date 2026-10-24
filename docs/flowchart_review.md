# Flowchart review notes for the first software pass

The initial algorithm images are useful reference material, but the project code uses the following corrected top-level routing:

1. The user selects **Sizing** or **Rating** first.
2. **Sizing** collects process requirements, validates inputs, runs the preliminary equipment-selection heuristic, and then routes to the selected exchanger's sizing function.
3. **Rating** bypasses equipment selection. The user chooses the exchanger type, enters operating conditions and existing geometry, and the selected rating function runs.
4. Each of the five exchanger types has distinct sizing, rating, thermal, hydraulic, and check modules. At present, the modules share simple common calculations and annotate the omitted type-specific physics.
5. Both paths end in a common results page with calculation trace, warnings, and exportable text/CSV summaries.

## Corrections intentionally deferred

The detailed flowcharts contain type-specific correlations and loop gates that should be transcribed only after the team agrees on the equation definitions, units, required variables, and reference source. This version does not silently invent those missing details. It instead uses marked placeholders for two-phase heat transfer, thermosyphon circulation, falling-film wetting, kettle pool boiling, pump curves, vapor disengagement, and code/mechanical checks.

The current equipment-selection ranking is a transparent heuristic to demonstrate the GUI route only. It should be replaced with the actual gates and constraints from the course's approved algorithm.
