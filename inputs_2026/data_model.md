# Data Model


## Residents

- Structure: N3 1-to-1 records
- file type : csv
```csv
| resident_name    | year | track \| (subtype) |
|------------------|------|--------------------|
| Doctor So-and-So | R2   | Standard           |
```
### Validation

- no name repeats
- year and track must be members of allowed years and tracks

## Rotations

- structure: `nested key-value`
- file type: `yaml`

### Example `rotations.yaml`

```yaml
Green HS Senior:
  min_residents: 1
  max_residents: 1
  unavailable_weeks: None # optional
Orange HS Senior:
  min_residents: 1
  max_residents: 1
Systems of Medicine:
  min_residents: 3
  max_residents: 6
  available_weeks: 
    - 2026-10-12
    - 2026-10-19
    - 2027-03-01
    - 2027-03-08
```

### Validation

- min_residents <= max_residents
- (exist(available_weeks) xor exist(unavailable_weeks)) or (~exist(available_weeks) and ~exist(unavailable_weeks))

## Requirements

- structure: `nested key-value -> successive inheritance-merges of requirement sets based on resident type`
- file type: `yaml`

### Example `R2_base_requirements.yaml`:

```yaml
HS Admitting Senior:
  constraints:
    - type: min_by_period
      weeks: 5
    - type: max_by_period
      weeks: 6
    - type: min_contiguity_in_period
      weeks: 2
  fulfilled_by:
    - Purple HS Senior
HS Rounding Senior:
  constraints:
    - type: min_by_period
      weeks: 2
    - type: max_by_period
      weeks: 4
    - type: min_contiguity_in_period
      weeks: 2
    - type: max_contiguity_in_period
      weeks: 4
    - prerequisite_fulfillers:
        - HS Admitting Senior
      type: prerequisite
      weeks: 2
    - type: respect_block_alignment
  fulfilled_by:
    - Green HS Senior
    - Orange HS Senior
```

### Validation:

- `fulfilled_by` and `prerequisite_fulfillers` must be members of `Rotations`
- min_by_period <= max_by_period; likewise for contiguity
