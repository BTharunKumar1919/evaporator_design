# Evaporator Design & Rating — working starter template

This repository provides a Python/Streamlit end-to-end scaffold for the team's evaporator/reboiler design project. It includes a GUI workflow, five exchanger modules, shared preliminary calculations, a rule-based selection placeholder, pressure-drop screening estimates, reports, and basic tests.

## 1. Included exchanger modules

- Falling Film Evaporator
- Forced Circulation Evaporator
- Vertical Thermosyphon Reboiler
- Horizontal Thermosyphon Reboiler
- Kettle Reboiler

Every exchanger has separate `sizing.py`, `rating.py`, `thermal.py`, `hydraulics.py`, and `checks.py` files. The exchanger-specific entry points currently route through common illustrative calculations so the complete workflow works before the team's detailed correlations are added.

## 2. Run the app

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

Streamlit prints a local URL (usually `http://localhost:8501`). Open it in a browser.

## 3. Workflow in the GUI

### Sizing
1. Select **Sizing**.
2. Enter process, thermal and hydraulic screening inputs.
3. The app ranks the five equipment types using a simple transparent heuristic. The team can override the highest-ranked choice.
4. Enter preliminary tube dimensions and run sizing.
5. Review required duty/area, calculated tube count, installed area, estimated capacity, pressure-drop proxies, warnings and downloadable reports.

### Rating
1. Select **Rating**.
2. Directly select one of the five exchanger types (selection algorithm is bypassed).
3. Enter process conditions and the existing exchanger geometry.
4. Review estimated heat capacity, achievable vapor fraction, pressure-drop proxies and checks.

## 4. Important model limitations

**This is a functioning software starter, not a validated design program. Do not use its outputs for purchasing, operation, safety certification, or final equipment design.**

The current common thermal model estimates:

- Sensible duty: `m_dot * Cp * max(T_boil - T_in, 0)`
- Latent duty: `m_dot * target_vapor_fraction * latent_heat`
- Effective LMTD from heating-medium inlet/outlet temperature and a constant process-side boiling temperature
- Required area using `Q / (U * LMTD * F)`
- Tube count from external tube area

The current pressure-drop model is a Darcy–Weisbach single-phase equivalent-channel proxy. The process-side path is assumed to be inside parallel tubes. **That assumption is inappropriate for several of the listed configurations and especially inappropriate for boiling/two-phase flow, falling films, pool boiling and natural-circulation loops.** Each exchanger module emits explicit warnings where the correct hydraulic model is still missing.

Other missing items include verified property packages, saturation properties as a function of pressure, heat-transfer correlations for each exchanger type, two-phase pressure drop, circulation-loop momentum balance, vapor disengagement/entrainment, mechanical/code checks, material selection, fouling/viscosity effects, and convergence/feasibility logic specific to each type. The equipment-selection ranking is only a placeholder and must be revised against the team's flowchart and approved references.

## 5. Where to work

| Path | Purpose |
|---|---|
| `app.py` | Mode wizard and page routing |
| `ui/forms.py` | Reusable process and geometry input forms |
| `ui/results.py` | Metrics, warnings, tables and downloads |
| `core/equipment_selection.py` | Placeholder selection heuristic to revise |
| `core/solver.py` | Dispatches to the selected exchanger module |
| `core/validation.py` | Basic input checks |
| `calculations/common/thermal.py` | Common duty/LMTD/area equations |
| `calculations/common/hydraulics.py` | Preliminary Darcy pressure-drop proxy |
| `calculations/evaporators/<type>/` | Per-exchanger entry points, model notes and checks |
| `reporting/report_generator.py` | Text and CSV report generation |
| `tests/` | Small calculation and routing tests |

## 6. Run tests

```bash
pytest -q
```

## 7. Suggested implementation sequence

1. Review every field in the GUI against the team's data-entry sheets.
2. Replace the equipment-selection heuristic with the flowchart's corrected rules.
3. Agree the thermal and hydraulic calculation contract for each exchanger type.
4. Validate the common energy balance/LMTD and unit conversions with hand calculations.
5. Implement one exchanger's sizing and rating equations, compare against an authoritative worked example, and only then duplicate the pattern to the other types.
6. Add meaningful reference cases and regression tests for every accepted equation/correlation.

The app intentionally keeps all calculations outside the GUI so the equations can be tested and reviewed independently.
