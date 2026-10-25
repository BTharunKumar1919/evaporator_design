# Flowchart review notes

The app's top-level route follows the requested course workflow:

1. User selects **Sizing** or **Rating**.
2. Sizing collects process requirements, validates inputs, runs the explicit equipment-selection gates, and then lets the user confirm or override the highest-ranked equipment type.
3. Rating bypasses selection and evaluates the user-selected equipment type with the entered geometry held fixed.
4. Each of the five equipment types has its own sizing/rating entry points and type-dependent checks. Common calculation orchestration is used to avoid duplicating shared duty, area and resistance equations.
5. The results page reports a calculation trace, source-specific checks and warnings, and exportable text/CSV summaries.

## Algorithms represented

- **Equipment selection:** viscosity/slurry/fouling/high-flux priority, heat sensitivity or low-approach preference, high exit vapour fraction and pressure-extreme gates, followed by natural-circulation/headroom/orientation rules. The result is a ranking with review cautions, not a certified hard rejection.
- **Forced circulation:** sensible plus latent duty; mixed sensible/latent LMTD as used in its examples; tube-side Reynolds/Prandtl/Nusselt and Dittus–Boelter HTC screen; resistance network; tube-count area gate; single-phase tube-friction and pump-power estimate.
- **Horizontal thermosyphon:** duty and area iteration; entered pool-boiling HTC with bundle/mixture factors; natural-circulation screen; CHF and 70%-of-CHF check; preliminary shell/bundle disengagement check.
- **Vertical thermosyphon:** duty and area iteration; entered effective boiling HTC; Zivi void-fraction/mixture-density and static-pressure screen; optional user-supplied loop-loss balance; CHF check and exit-quality gate.
- **Kettle:** pool-boiling/bundle calculation; area gate; CHF check; fixed-geometry shell disengagement rule.
- **Falling film:** film wetting-rate/Reynolds/Prandtl/regime HTC calculation; area iteration; Palen dry-out and minimum-wetting checks; distributor-head and approximate Wallis flooding screens.

## Corrections and unresolved source issues

The shared engine deliberately does not imply that every formula is a complete or independently validated correlation. The uploaded Mostinski equation/substitution is not reproducible as written; the Chen example does not provide enough details to independently calculate all terms; natural-circulation friction and acceleration losses are unavailable unless supplied; and several numerical examples have small arithmetic or gate inconsistencies. The program exposes such limitations rather than concealing them. Refer to `all_algorithms_review_and_worked_examples.md` for the documented discrepancies and numerical checks.
