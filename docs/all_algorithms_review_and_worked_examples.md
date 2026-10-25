# Review of the Uploaded Evaporator/Reboiler Algorithms and Numerical Examples

## Purpose and scope

This review compares the uploaded selection algorithm, five equipment algorithms, and their sizing/rating examples with the implementation in this project. The implementation is a **preliminary educational model**. It now has different calculation paths for the five equipment types, reports equipment-specific screening checks, and exposes source ambiguities. It is not a certified exchanger design, a TEMA mechanical design, or a substitute for a validated two-phase flow model.

The program does not claim that every correlation in the PDFs can be reproduced exactly. Where an example supplies an HTC as an assumption but does not give enough consistent information to recalculate it, the corresponding HTC is an explicit input. This is preferable to inventing a calculation and labelling it as the source's method.

---

## 1. Shared thermal basis and area gate

The common duty basis used by the numerical examples is:

- Sensible heating: `Qsens = m_dot_feed * Cp * max(Tboil - Tin, 0)`.
- Latent duty: `Qlat = m_dot_vapour * h_fg`. By default `m_dot_vapour = m_dot_feed * xe`; a new optional **vaporization-rate override** lets the user enter the separate vapour generation rate used by examples that state it independently. `xe` remains the separate exit-quality/selection input.
- Total duty: `Q = Qsens + Qlat`.
- Required area: `Areq = Qdesign / (Uo * ΔTeff)`.
- Installed outside tube area: `Acalc = Nt * π * do * L`.
- Sizing area gate: normally `1.10 <= Acalc/Areq <= 1.20`; the falling-film example permits up to `1.25`.

`design_margin` is an extra multiplier on duty; it defaults to 1.0 because the source algorithms already add the required area allowance through the area gate. Do not set a second 10–20% design-margin multiplier unless your course instructions require it.

### Temperature-difference basis is equipment-specific

The source forced-circulation examples use a mixed sensible/latent LMTD:

`ΔT1 = Th,in - Tfeed,in`, `ΔT2 = Th,out - Tboil`, then `LMTD = (ΔT1 - ΔT2)/ln(ΔT1/ΔT2)`.

The other four example sets use a constant-boiling-temperature approach in their provisional calculations. The code now makes that difference explicit. It still assumes a single correction factor `F`; it does not model a full multi-zone exchanger or property variation with pressure.

The overall coefficient is calculated on outside tube area using separate convection, fouling, and tube-wall resistance terms. For pool-boiling shells, the code uses the entered baseline boiling HTC and applies the supplied bundle/mixture factors; see the limitation under those equipment sections.

---

## 2. Equipment selection algorithm and two worked examples

### Decision logic represented in the code

1. **Gate 1 — forced circulation priority:** high viscosity (50 cP or more), slurry/crystallising service, process-side fouling factor at or above `0.0004 m²·K/W`, or a high-heat-flux flag.
2. **Gate 2 — temperature-sensitive service / small approach:** heat-sensitive or thermally unstable product, or `ΔTeff <= 8 °C`. Falling film is preferred when vertical headroom is at least 4.5 m; restricted headroom changes the preferred fallback.
3. **Gate 3 — high exit vapour fraction / pressure extremes:** `xe >= 0.35`, near-critical process pressure (when the critical pressure is known), or deep vacuum at or below `0.15 bar abs`. Clean service with narrow boiling range favours kettle in the source's sub-gate; otherwise forced circulation is prioritised.
4. **Gate 4 — natural circulation and orientation:** where no prior gate dominates, compare any user-provided loop-loss estimate against the available driving head/allowable pressure drop and use headroom, floor-space and duty considerations to rank the thermosyphon orientations.

The result is a **ranking and review trace**, not an automatic certified rejection. User choice is retained. If frictional/acceleration loss for a natural-circulation loop is not supplied, the code says `UNKNOWN` rather than pretending a two-phase loop balance has been solved.

### Worked example A — equipment allocation example in the supplied PDF

Source inputs: feed `15 kg/s`, exit vapour `3.75 kg/s`, `xe = 0.25`, boiling/feed temperature `92.5 °C`, `hfg = 345 kJ/kg`, heating temperatures 145/130 °C, `rho_l = 565 kg/m³`, static elevation `1.8 m`, viscosity `0.21 cP`, process fouling `0.0001 m²·K/W`, boiling range `6.5 °C`, process pressure `3.5 bar abs`, headroom `3.2 m`, estimated loop loss `6.2 kPa`, allowable pressure drop `35 kPa`.

Calculations:

- `R = (1 - xe)/xe = 3`.
- Sensible duty is zero because feed is already at the stated boiling temperature.
- `Q = 3.75 * 345 = 1293.75 kW`.
- Mean heating temperature is `137.5 °C`; `ΔTeff = 137.5 - 92.5 = 45 °C` under the selection pre-processing rule.
- Static head: `rho*g*H = 565*9.81*1.8 = 9.98 kPa`.
- The estimated loop loss `6.2 kPa` is below this static-head screen and below the stated allowable pressure drop.
- With gates 1–3 untriggered and headroom below `4.5 m`, Gate 4 favours the **Horizontal Thermosyphon Reboiler**, consistent with the worked example's TEMA G-shell choice.

The code keeps this pre-processing calculation separate from the more detailed equipment sizing calculation. The selector's static-head comparison is a simplified course gate, not a full loop momentum balance. In sizing/rating, the horizontal thermosyphon uses this same source static-head/allowable-ΔP screen and does not incorrectly count the full horizontal tube length as a vertical two-phase gravity head.

### Worked example B — aqueous/deep-vacuum example

Source inputs: feed `8.5 kg/s`, `xe = 0.25`, `Tin = 30 °C`, `Tboil = 45.8 °C`, `Cp = 4.184 kJ/(kg·K)`, `hfg = 2390 kJ/kg`, heating temperature `119.6 °C`, process pressure `0.10 bar abs`, process fouling `0.00015 m²·K/W`, boiling range `1.2 °C`, static elevation `0.8 m`.

Using the printed equation and values:

- `Qsens = 8.5 * 4.184 * (45.8 - 30) = 561.91 kW`.
- `Qlat = (8.5 * 0.25) * 2390 = 5078.75 kW`.
- `Qtotal = 5640.66 kW`.
- `ΔTeff` under the selection rule is `119.6 - 45.8 = 73.8 °C`.
- Static head is `990 * 9.81 * 0.8 = 7.77 kPa` if the example's liquid density is `990 kg/m³`.

Gate 3 triggers on deep vacuum; the clean-service/narrow-boiling-range sub-gate favours the **Kettle Reboiler**, consistent with the sample's selection.

### Selection example discrepancies to retain

- The PDF reports `Qsens = 561.304 kW` and `Qtotal = 5640.054 kW`, whereas its stated inputs and equation give approximately `561.91 kW` and `5640.66 kW`. The implementation follows the stated equation and inputs, not hard-coded reported numbers.
- The justification text recommends a vacuum recirculation ratio around `15–18` (elsewhere roughly `10–25`), but the worked example uses `xe = 0.25`, giving `R = 3`, and selects kettle. The code displays a consistency warning and does not silently change `xe`.
- The horizontal-thermosyphon sizing example below uses `xe = 12/30 = 0.40`, which triggers the separate selection Gate 3 (`xe >= 0.35`). That is a conflict between a pre-selected equipment sizing example and the selector's general recommendation rule; it is not a reason to rewrite the sizing example.

---

## 3. Forced-circulation evaporator

### Algorithm path in the code

1. Calculate sensible and latent duty.
2. Use the source mixed sensible/latent LMTD.
3. Select a provisional tube count from a seed overall coefficient, then calculate tube velocity/flow rate from the entered/target circulation velocity.
4. Calculate tube-side `Re`, `Pr`, `Nu` and Dittus–Boelter HTC.
5. Combine process-side and heating-side HTCs with outside-area-referenced fouling/wall resistances.
6. Iterate tube count until the 10–20% area gate is reached.
7. Screen tube-side frictional pressure drop and pump hydraulic power. The friction proxy is single-phase; it omits two-phase acceleration and boiling effects.

### Worked example — sizing

Source inputs: feed `10 kg/s` at `80 °C`, boiling at `100 °C`, `xe = 0.10`, `hfg = 2260 kJ/kg`, `Cp = 4180 J/(kg·K)`, saturated steam at `120 °C` in/out, `do = 25.4 mm`, `di = 21.1 mm`, `L = 3 m`, circulation velocity `3 m/s`. Leave the vaporization-rate override at zero; `10 × 0.10 = 1 kg/s` matches the source vapour rate.

- `Qsens = 10 * 4180 * (100 - 80) = 836 kW`.
- `Qlat = 1 * 2260 = 2260 kW`.
- `Qtotal = 3096 kW`.
- Mixed LMTD: `ΔT1 = 120 - 80 = 40 K`; `ΔT2 = 120 - 100 = 20 K`; `LMTD = 20/ln(2) = 28.85 K`.
- Using `Uguess = 1200 W/(m²·K)`, provisional area is `89.4 m²`; at `3 m` tube length the initial count is about `374` tubes.
- With `rho = 960 kg/m³`, `mu = 0.00028 Pa·s`, `k = 0.68 W/(m·K)`, `Pr = 1.72`, source correlation gives `Re ≈ 217,028`, `Nu ≈ 530` and `hi ≈ 17,080 W/(m²·K)`.
- The source assumes heating-side HTC `ho ≈ 5150 W/(m²·K)` and gets `Uo ≈ 1538 W/(m²·K)`, required area `69.8 m²`.
- At `Nt = 320`, installed area is `76.6 m²` and ratio is `76.6/69.8 = 1.097` — **just below** the literal 1.10 lower limit, despite the PDF calling it approximately a 10% pass. The code follows the numerical gate and warns if the ratio is below 1.10.

### Worked example — rating

The PDF's rating example gives `Nt = 200`, `do = 19.05 mm`, `L = 4 m`, flow rate `0.05 m³/s`, feed `5 kg/s`, vapour target `0.5 kg/s`, `Tin = 60 °C`, `Tboil = 80 °C`, `hfg = 350 kJ/kg`, `Cp = 2500 J/(kg·K)`, `rho = 800 kg/m³`, `mu = 0.0005 Pa·s`, `k = 0.15 W/(m·K)`, `Pr = 8.3`, and hot side at `110 °C`.

- Duty: `5*2500*(80-60) + 0.5*350000 = 425 kW`.
- LMTD: `(50-30)/ln(50/30) = 39.15 K`.
- Installed outside area: `200*π*0.01905*4 = 47.88 m²`.
- Source HTC/overall-U estimates give `Uo ≈ 735 W/(m²·K)` and capacity around `1.38 MW`, around `224%` above duty. The program recalculates based on the actual property and HTC inputs entered in the form, so matching this number requires entering the example's properties and heating HTC.

### Forced-circulation limitations

The Dittus–Boelter correlation assumes turbulent single-phase forced convection; actual boiling suppression, wall-temperature iteration, and two-phase pressure losses are not solved. The code reports the assumption instead of treating the tube friction estimate as the total system pressure drop.

---

## 4. Horizontal thermosyphon reboiler

### Algorithm path

1. Calculate duty and preliminary area.
2. Estimate bundle diameter from tube count, pitch and an explicitly approximate layout rule.
3. Use the entered baseline nucleate pool-boiling HTC, apply bundle and mixture factors, add the natural-convection term, then calculate overall U.
4. Iterate tube count against the 10–20% area gate.
5. Run the source's natural-circulation static-head/allowable-ΔP screen (not a full riser/downcomer momentum balance), CHF/70% allowable-flux screening and the bundle/shell-diameter disengagement screen.

### Worked example — sizing

Source inputs: vapour `12 kg/s`, liquid feed `30 kg/s`, `Tsat = 65 °C`, feed `60 °C`, steam `110 °C`, `hfg = 330 kJ/kg`, `Cp = 2.6 kJ/(kg·K)`, `rho_v = 14.5 kg/m³`, `rho_l = 480 kg/m³`, `sigma = 0.009 N/m`, `P = 18 bar`, `Pcrit = 42.5 bar`, boiling range zero.

- `Q = 12*330 + 30*2.6*(65-60) = 4350 kW`. In the updated form enter `mass flow = 30 kg/s`, `vaporization-rate override = 12 kg/s`, and `xe = 0.40`; the override reproduces the specified vapour duty while `xe` continues to drive the quality gate.
- `ΔTeff = 110 - 65 = 45 K`.
- With `Uguess = 1200 W/(m²·K)`, `Areq ≈ 80.5 m²`.
- For `do = 25.4 mm`, `L = 6 m`, square pitch `Pt = 1.25 do = 31.75 mm`, and `Nt = 180`, `Acalc ≈ 86.0 m²`; the example estimates bundle diameter `Db ≈ 0.468 m`.
- The source gives `hnb ≈ 5340 W/(m²·K)`, bundle factor `Fb ≈ 1.48`, `Fs = 1`, and boiling HTC including natural convection around `8153 W/(m²·K)`. With the source's heating HTC and resistance assumption, `Uo ≈ 1855 W/(m²·K)` and `Areq ≈ 52.1 m²`.
- At about `125` tubes the source says the converged installed area is around `60 m²`, ratio `60/52.1 ≈ 1.151` (within the 10–20% gate).
- The source reports tube CHF `≈ 416.6 kW/m²`, bundle CHF `≈ 158.3 kW/m²`, and 70% allowable bundle flux `≈ 110.8 kW/m²`; operating flux is below this source screen.

### Worked example — rating

The source rating example specifies `Qreq = 2.5 MW`, `Nt = 100`, `do = 19.05 mm`, `L = 4 m`, area `≈23.9 m²`, `Db = 0.28 m`, `ΔT = 28 K`, heating HTC `1400 W/(m²·K)`, fouling `0.0004 m²·K/W`, process `rho_v = 1.2`, `rho_l = 940 kg/m³`, `hfg = 2200 kJ/kg`, and surface tension `0.05 N/m`.

The source result has `Uo ≈ 829 W/(m²·K)` and capacity `≈0.555 MW`, so it fails the `2.5 MW` thermal target. Its source CHF check is separate from the thermal capacity gate; passing one would not repair failure of the other.

### Source equation limitation

The supplied Mostinski equation/substitution has inconsistent units/arithmetic, so the program does **not** label an automatically generated value as a verified Mostinski result. The baseline pool-boiling HTC is a visible input; bundle/mixture factors are calculated and displayed. This means the user must enter a justified `hnb` value to reproduce each specific numerical example.

---

## 5. Vertical thermosyphon reboiler

### Algorithm path

1. Calculate duty and constant-boiling LMTD.
2. Estimate tube count from a seed U; use an explicit effective boiling HTC input (the source example gives a Chen result but not enough information to independently reconstruct every term).
3. Iterate area gate.
4. Estimate Zivi void fraction / mixture density and static driving pressure; compare with a supplied estimate for friction plus acceleration loss only when one is available.
5. Calculate CHF and check operation below 70% of bundle CHF; enforce the source's exit-quality cap `xe <= 0.25`.

### Worked example — sizing

Source inputs: `1 kg/s` vapour at `hfg = 2257 kJ/kg`, `1 kg/s` liquid feed, `Cp = 4.2 kJ/(kg·K)`, `Tfeed = 95 °C`, `Tsat = 100 °C`, `ΔTeff = 30 K`.

- `Q = 2257 + 1*4.2*5 = 2278 kW`.
- With `Uguess = 2000 W/(m²·K)`, provisional `Areq ≈ 37.96 m²`.
- `do = 25.4 mm`, `L = 2.5 m` gives area per tube about `0.1995 m²`; the first 210-tube geometry gives only `41.8 m²`, below `1.10*53.9 m²` after the detailed U result, so the source iterates upwards.
- With the example HTC values, `Uo ≈ 1408 W/(m²·K)`, `Areq ≈ 53.9 m²`; the source proposes `310` tubes, `Acalc ≈ 61.8 m²`, ratio `≈1.147` (pass).
- The example uses `1.5 m` sump head: liquid static pressure `≈14.10 kPa`; the PDF reports gravity loss `≈4.24 kPa` and friction plus acceleration loss `≈9.8 kPa`, summing to `≈14.04 kPa`.
- Source CHF: tube `≈1.12 MW/m²`; bundle `≈448 kW/m²`; operating flux `≈36.8 kW/m²` is below `70%` of bundle CHF. Exit quality around `0.105` is below `0.25`.

**Source discrepancy:** the justification PDF's printed Zivi equation uses the `2/3` density-ratio exponent. At `x = 0.10`, `rho_l = 958 kg/m³`, and `rho_v = 0.598 kg/m³`, that expression gives `alpha ≈ 0.94`, not the example's `alpha ≈ 0.82`. It also gives a much lower mixture density/gravity head than the example's `172.9 kg/m³` and `4.24 kPa`. The implementation follows the printed equation and adds a result warning for the matching example conditions; it does not tune alpha to force the published pressure balance.

### Worked example — rating

The toluene rating example asks for `1.2 MW`, `Tsat = 110 °C`, steam at `150 °C`, `Nt = 200`, `do = 19.05 mm`, `L = 3 m`, area `≈35.9 m²`, process HTC `1200 W/(m²·K)`, heating HTC `6000 W/(m²·K)`, and fouling `0.0004 m²·K/W`.

The source estimates `Uo ≈ 714 W/(m²·K)` and capacity `≈1.025 MW`, so the thermal rating fails. It separately estimates natural-loop driving pressure `≈14.126 kPa`, gravity loss `≈7.357 kPa`, and remaining friction/acceleration allowance `≈6.769 kPa`. Its CHF operating flux `≈28.5 kW/m²` is below `70%` of the source's bundle-CHF estimate `≈85 kW/m²`.

### Vertical-thermosyphon limitations

The code does not pretend to solve the entire Chen correlation from missing properties and correlation details. The effective boiling HTC is an explicit input. Natural-circulation balance is labelled unknown if the user has not supplied a defensible friction/acceleration estimate. A constant-density mixture is a screening approximation, not a full two-phase momentum model. The source independently states vapour generation and exit quality; the vaporization-rate override was added so those two quantities can be entered separately.

---

## 6. Kettle reboiler

### Algorithm path

1. Compute duty/area and tube-bundle geometry.
2. Use entered baseline pool-boiling HTC, bundle factor, mixture factor and natural-convection term for the boiling-side HTC.
3. Iterate tube count to the area gate.
4. Apply the source CHF screen.
5. Check shell diameter against the source disengagement minimum `Ds >= 1.4*Db + 0.10 m`; rating keeps user-entered geometry fixed and must not auto-correct a deficient shell.

### Worked example — sizing

Source propane case: vapour rate `10 kg/s`, `hfg = 300 kJ/kg`, `Q = 3 MW`, `ΔT = 40 K`, `Uguess = 1200 W/(m²·K)`.

- `Areq,seed = 3,000,000/(1200*40) = 62.5 m²`.
- Initial `Nt = 280`, `do = 25.4 mm`, `L = 3 m` gives `Acalc ≈67.0 m²`, bundle diameter around `0.65 m`.
- The source estimates `hnb ≈3850 W/(m²·K)`, `Fb ≈1.63`, `hnc ≈250 W/(m²·K)`, and boiling HTC `≈6525 W/(m²·K)`. With the stated heating-side HTC/resistance assumptions, it obtains `Uo ≈1730 W/(m²·K)`, `Areq ≈43.3 m²`.
- The source reduces tube count to `200`, area `≈47.8 m²`, ratio `≈1.104`, which is within the 1.10–1.20 area gate.
- However, the source's CHF arithmetic gives tube CHF `≈360 kW/m²`, bundle factor `φb≈0.057`, bundle CHF `≈20.52 kW/m²`, and 70% allowable `≈14.36 kW/m²`; operating flux `≈62.76 kW/m²` therefore **fails**. Meeting the thermal area gate does not mean the kettle passes CHF.

### Worked example — rating

Source inputs: `1.5 kg/s` vapour, `hfg = 2257 kJ/kg`, target duty `3.3855 MW`; hot-oil mean `160 °C`, `ΔT = 60 K`; `Nt = 300`, `do = 20 mm`, `L = 4 m`, `Db = 0.6 m`, `Ds = 0.9 m`, installed area `75.4 m²`; source HTCs `2500` and `8200 W/(m²·K)`, total fouling `0.0003 m²·K/W`.

- Source `Uo ≈1219 W/(m²·K)` and capacity `≈5.51 MW`, so thermal capacity passes.
- Shell disengagement screen requires `Ds >= 1.4*0.6 + 0.10 = 0.94 m`; the entered `0.90 m` shell **fails**, despite adequate calculated thermal capacity.

### Kettle limitation

As with horizontal thermosyphon, the baseline pool-boiling HTC must be supplied or independently justified because the PDF's Mostinski arithmetic is not reproducible as written. The code does not conflate an area pass, a CHF pass, and a shell disengagement pass.

---

## 7. Falling-film evaporator

### Algorithm path

1. Calculate duty, constant-boiling LMTD and starting tube count.
2. Calculate tube-side film mass-flow rates per wetted perimeter at inlet/outlet, film Reynolds and Prandtl numbers, estimated film thickness and the source's regime-dependent heat-transfer correlation.
3. Calculate area/U and iterate tube count to the 10–25% sizing area band.
4. Check minimum outlet wetting rate, Palen dry-out criterion, distributor head (`25–200 mm` source screen), and an approximate Wallis flooding parameter.

### Worked example — sizing

Aqueous sugar case: `mfeed = 8 kg/s`, evaporated `2 kg/s`, `Tb = Tin = 90 °C`, `hfg = 2283 kJ/kg`, saturated steam at `105 °C`, `ΔT = 15 K`.

- `Q = 2*2283 = 4566 kW` (sensible duty is zero under the stated input temperatures). Either leave the override at zero with `mdot = 8 kg/s, xe = 0.25`, or enter `2 kg/s` explicitly; both give the same latent duty.
- With `Uguess = 2000 W/(m²·K)`, the starting area is `4566/(2000*15) = 152.2 m²`.
- The source starts with `do = 38.1 mm`, `di = 34.9 mm`, `L = 6 m`, and around `212` tubes. It reports inlet wetting rate about `0.344 kg/(m·s)`, outlet wetting rate about `0.258 kg/(m·s)`, mean `0.301 kg/(m·s)`, `Re_f ≈3010`, and `Pr ≈2.58` for its first trial.
- The source's later thermal convergence states `Areq ≈261.2 m²` at `U ≈1165 W/(m²·K)`. The first area-gate check is undersized (`Acalc` is below `1.10*Areq`); its later target area at 15% overdesign is stated around `300.4 m²`, corresponding to roughly `419` tubes with those dimensions.
- Palen dry-out screen: source `Fkl = Γin*hfg = 0.344*2,283,000 ≈785,352 W/m`; the code compares this with `1.5*qL` and separately checks minimum outlet wetting rate.

The PDF's intermediate figures are not perfectly self-consistent, so the source's stated converged area and tube count should be treated as a reported example rather than an exact regression target. In the form use `vaporization-rate override = 2 kg/s` and `xe = 0.25` to specify the stated vapour duty and the separate exit-quality input. The app recalculates from the input data.

### Worked example — rating

Source rating case: `Nt = 300`, `do = 25.4 mm`, `di = 21.1 mm`, `L = 4 m`, area `≈95.75 m²`, required duty `1.2 MW`, `hfg = 400 kJ/kg`, inlet wetting `Γin ≈0.301 kg/(m·s)`, `Re_f ≈2189`, viscosity `0.00055 Pa·s`, `Pr ≈8.64`, `Recrit ≈597`. The source uses a turbulent-film HTC of `≈1341 W/(m²·K)` and `Uo ≈655.7 W/(m²·K)`.

- `Qmax = U*A*ΔT = 655.7*95.75*40 ≈2.51 MW`.
- Source overdesign relative to `1.2 MW` is `≈109.2%`, so thermal capacity is adequate with substantial overdesign.
- Source Palen quantities: `Fkl = 120,400 W/m`, `1.5*qL = 90,504 W/m`; dry-out criterion passes.
- Distributor sizing uses the specified orifice count/diameter/discharge coefficient. The source recommends liquid head roughly `25–200 mm`.
- The source also asks that vapour velocity remain below about `75%` of its flooding-velocity estimate. The implemented Wallis metric is deliberately labelled approximate because the user-facing inputs do not describe the full two-phase core geometry.

### Falling-film limitations

The wetted perimeter depends on tube count/diameter and the method is sensitive to correct process-side tube/shell allocation. Minimum wetting rate is a user input because the acceptable value is fluid/surface dependent. The Wallis check is a warning screen only, not a complete flooding model.

---

## 8. Cross-equipment limitations and exact files changed

The implementation covers the reproducible pieces of all five algorithms, but the following are still estimates or explicit inputs, not solved physics:

- No detailed two-phase friction, acceleration, static head distribution or full natural-loop momentum model; loop loss must be supplied to evaluate the balance.
- No complete Chen boiling calculation from unavailable inputs; effective coefficient is explicit for vertical thermosyphon.
- No claim to calculate the Mostinski baseline from its inconsistent printed formula/substitution; baseline HTC is input for horizontal/kettle.
- CHF equations are implemented as course-algorithm screening formulas and must be checked against the exact unit convention and validity range intended by the course material.
- Bundle diameter uses a simple `Db ≈ 1.1 sqrt(Nt) Pt` estimate, not a full TEMA layout calculation.
- Shell disengagement is a preliminary screen; this is not a complete nozzle, vapor-space, weir, entrainment or mechanical design.
- Tube wall thickness screen does not establish ASME compliance; detailed design also needs material-specific allowable stress, corrosion/erosion allowance, joint efficiency, design conditions, external pressure, tube-sheet and other mechanical checks.
- Heating-side pressure drop is a single-phase estimate; process-side two-phase drop is deliberately reported as uncalculated when no valid equipment-specific method is available.
- The source examples sometimes mix input properties from different illustrative cases. Reproduction requires entering the actual example's property values and assumed HTCs, not only geometry.

### Files updated in this version

- `core/equipment_selection.py`
- `core/models.py`
- `core/validation.py`
- `app.py`
- `ui/forms.py`
- `ui/results.py`
- `reporting/report_generator.py`
- `calculations/common/engineering_models.py`
- `calculations/common/sizing.py`
- `calculations/common/rating.py`
- all `calculations/evaporators/<equipment>/{sizing,rating,checks,thermal,hydraulics}.py` adapters for the five equipment types
- `tests/test_algorithm_source_alignment.py`

Use the same relative paths when replacing the files in your project.
