# Workflow at a glance

```text
START
  |
  v
Select SIZING or RATING
  |                                  |
  | SIZING                           | RATING
  v                                  v
Enter process requirements           Select exchanger type directly
  |                                  |
Validate inputs                      Enter operating conditions + geometry
  |                                  |
Rank eligible/likely exchanger types Run selected type's rating module
  |
Choose/override type
  |
Enter preliminary geometry preferences
  |
Run selected type's sizing module
  |                                  |
  +------------------+---------------+
                     v
       Thermal results + pressure-drop proxies
                     |
       Warnings, checks, trace and report export
                     |
                    END
```

The selection ranking and five equipment-specific calculation paths follow the uploaded course algorithms where source equations are reproducible. Correlation limitations, unavailable two-phase losses and worked-example inconsistencies are documented in `docs/all_algorithms_review_and_worked_examples.md`.
