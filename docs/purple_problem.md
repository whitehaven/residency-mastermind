# purple problems

> Status: Possibly completed

## Problem Statement

After review 2/9, observation made that only certain things can follow Purple due to Sunday workday.

Classically takes the form of `Purple -> Consults` which is a natural fit, but could come before Elective or Clinic.

```mermaid
graph LR
;
    Consults --> Purple -->|ideal| Consults 
    Purple --> Elective & Consults
    Purple --> E[End of Year]
    Purple --x HS & ICU & Purple & Vacation
```

## Solution

Added constraint as above, verified working with real 2026 data.

May be though that desired behavior is P -> Elective|Consults -> P -> Elective|Consults. Will ask for confirmation.