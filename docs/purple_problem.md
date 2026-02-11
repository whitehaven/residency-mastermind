# purple problems

After review 2/9, observation made that only certain things can follow Purple due to Sunday workday.

Classically takes the form of `Purple -> Consults` which is a natural fit, but could come before Elective or Clinic.

```mermaid
graph LR
;
    Consults --> Purple -->|ideal| Consults 
    Purple --> Elective
    Purple --> E[End of Year]
    Purple --x HS & ICU & Purple & Vacation
```