# Evaporator Design & Rating — preliminary course-algorithm implementation

This Streamlit project implements a transparent preliminary workflow for five evaporator/reboiler types:

- Falling Film Evaporator
- Forced Circulation Evaporator
- Vertical Thermosyphon Reboiler
- Horizontal Thermosyphon Reboiler
- Kettle Reboiler

Sizing collects process requirements, applies the rule-based equipment-selection gates, and lets the user confirm or override the ranked choice. Rating bypasses equipment selection and evaluates the specified equipment and existing geometry.

The five type-specific folders provide separate sizing/rating entry points. Shared orchestration is in `calculations/common/engineering_models.py`; equipment-specific methods, checks, and assumptions are shown in the app and in the review document.

## Run the app

Use Python 3.10 or newer. From this folder, create and activate a virtual environment, then install dependencies.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`). On Windows you can use `setup_windows.bat` and `run_app.bat` instead.

## Workflow

### Sizing
1. Choose **Sizing**.
2. Enter process, property, temperature, fouling, pressure, and selection inputs.
3. Review the equipment-selection gates, ranked candidates and cautions.
4. Confirm an equipment type, enter preliminary geometry, and run sizing.
5. Review the area gate, equipment-specific checks, warnings and downloadable report/CSV.

### Rating
1. Choose **Rating**.
2. Choose an equipment type directly; the selection algorithm is bypassed.
3. Enter operating conditions and existing geometry. Rating does not auto-correct the stated tube count, shell or bundle dimensions.
4. Review thermal capacity and separate hydraulic, CHF, wetting, disengagement and mechanical screening results where relevant.

## Model limits — read before interpreting results

**This is an educational preliminary design aid, not a validated process simulator or mechanical-code design. Do not use it for procurement, operation, safety approval or final equipment design.**

The software follows the uploaded course algorithms where equations and inputs are reproducible. It explicitly exposes several assumptions rather than claiming a complete correlation calculation when the source documents do not support one:

- Forced circulation uses the source's mixed sensible/latent LMTD, Dittus–Boelter single-phase HTC screening and a Darcy tube-friction estimate. Boiling suppression, full wall-temperature convergence and two-phase pressure drop are not modelled.
- Horizontal thermosyphon and kettle use an entered baseline pool-boiling HTC because the supplied Mostinski formula/substitution has unit/arithmetic inconsistencies. The code displays its bundle/mixture factors but does not label the entered baseline as a verified Mostinski result.
- Vertical thermosyphon uses a separately entered effective boiling HTC because the example does not provide sufficient reproducible data for every Chen-correlation term.
- Natural-circulation friction and acceleration losses are not fabricated. The loop balance remains unknown unless a defensible loss estimate is supplied.
- CHF, disengagement, distributor and flooding calculations are preliminary course-algorithm screens. The bundle-diameter shortcut is not a full TEMA tube-layout calculation.
- Wall thickness is only an elementary pressure-thickness screen when design pressure/material data are entered. It does not establish ASME/TEMA compliance.
- Heating-side pressure drop is a single-phase estimate. Equipment-specific process-side two-phase losses are reported as not calculated where the current inputs/model do not support a credible result.

See [`docs/all_algorithms_review_and_worked_examples.md`](docs/all_algorithms_review_and_worked_examples.md) for the comparison with all uploaded algorithms and sizing/rating examples, the worked selection cases, numerical discrepancies and limitations.

## Important files

| Path | Purpose |
|---|---|
| `app.py` | Streamlit mode wizard and page routing |
| `ui/forms.py` | Process, property and geometry input forms |
| `ui/results.py` | Result metrics, engineering checks, warnings, report downloads |
| `core/equipment_selection.py` | Equipment-selection gates, rankings and calculation trace |
| `core/models.py` | Equipment names and default inputs |
| `core/validation.py` | Input validation |
| `core/solver.py` | Routes sizing/rating to the equipment-specific modules |
| `calculations/common/engineering_models.py` | Shared orchestration and equipment-specific physical screens |
| `calculations/common/thermal.py` | Duty and base LMTD equations |
| `calculations/common/hydraulics.py` | Heating-side and simple single-phase pressure-drop tools |
| `calculations/evaporators/<type>/` | Equipment-specific sizing, rating and supporting adapters |
| `reporting/report_generator.py` | Text and CSV reporting |
| `docs/all_algorithms_review_and_worked_examples.md` | Algorithm comparison and worked examples |
| `tests/` | Unit and source-example regression checks |

## Run tests

```bash
python -m compileall -q .
pytest -q
```

The tests verify that all five routes work, basic equations remain consistent, the forced-circulation source LMTD is reproduced, and the two equipment-selection worked examples return the expected top-ranked equipment. Passing these tests does not validate the empirical correlations or establish mechanical/process safety.
