UPDATED EVAPORATOR DESIGN / RATING PROJECT

Two ZIPs are provided:
1. evaporator_design_updated_full.zip: complete updated project, ready to extract and run.
2. evaporator_design_replacement_files.zip: only new/changed files, with paths relative to the existing evaporator_design/ folder.

To apply the replacement-files ZIP:
- Make a backup of your existing project folder.
- Extract the ZIP.
- Copy its core/, calculations/, ui/, reporting/, tests/ and docs/ folders, plus app.py and README files, into your existing evaporator_design/ folder.
- Preserve the folder structure and allow overwrite of same-named files.
- The ZIP includes new documentation and regression tests as well as the changed Python files.

To run from the project folder:
    python -m pip install -r requirements.txt
    streamlit run app.py

To verify calculation routes:
    python -m compileall -q .
    pytest -q

This is a preliminary educational model. Read docs/all_algorithms_review_and_worked_examples.md before interpreting values. It flags source-document arithmetic/correlation inconsistencies and cannot certify process or mechanical safety.
