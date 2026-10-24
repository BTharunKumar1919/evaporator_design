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

The selection ranking and five type-specific models are placeholders pending equation/correlation review.
