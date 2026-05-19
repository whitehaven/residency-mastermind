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
  available_weeks: # should mark any excluded weeks as unavailable
    - 2026-10-12
    - 2026-10-19
    - 2027-03-01
    - 2027-03-08
```

### Validation

- datatypes must match
- `min_residents <= max_residents`; min* must be below max*, etc.
- no overlap of available/unavailable risks

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

### Special problem: Inheritance Merge for Specific Requirement Sets

See `refactor_data_auxiliary_files/scratch_inheritance.py`. Merge uses `mergedeep` library.

### Validation:

- `fulfilled_by` and `prerequisite_fulfillers` must be members of `Rotations`
- min_by_period <= max_by_period; likewise for contiguity
- constraints must exist
- prerequisites_fulfillers must be member of relevant requirements

## Overrides

```csv
resident,rotation,week,overriding_value,comment
Resident,Vacation,2026-07-27,True,previously granted vacation
```

### Validation

- `resident`, `rotation`, `week` ∈ respective sets
- `overriding_value` ∈ boolean
- Error on duplicates of `resident` & `rotation` & `week`

## Requests (comprises vacations)

Opted for `csv` since all requests can be expressed as a range of weeks.

> Note vacations are expressed here as well - it's a rotation just like any other.

```csv
resident,rotation,week_start,week_end,request_polarity,priority
Resident A,Elective,2026-07-06,2026-07-27,preference,high
Resident B,ICU Senior,2026-09-14,2026-10-05,avoidance,high
Resident C,Vacation,2026-
```

> I am not in love with the `priority` column, but it makes sense for now.

### Validation

- `resident`, `rotation`, `week_start`,`week_end` ∈ respective sets
- `request_polarity` ∈ preference/positive | avoidance/negative
- `priority` ∈ high/medium/low
- when `week_start` and `week_end` are equal, optimality bonus/penalty is applied
- when `week_start` and `week_end` are not equal, unclear what to do with bonus/penalty - probably would divide over
  minimum size of rotation - see below.

### Future Directions

- Would be easy to map to requests entered by residents.

### Handling of multi-week bonus/penalty

The primary issue is of fairness between residents - if the same penalty or bonus was applied in a multi-week case, this
would advantage that resident because multiple weeks will stack.

For example, if we were trying to incentivize placing a person on ICU early while someone else asks for vacation. We'll
say weeks 1-6 are "early".

#### Naive

| Week            | 1  | 2  | 3  | 4  | 5  | 6  |
|-----------------|----|----|----|----|----|----|
| ICU Wanter      | 10 | 10 | 10 | 10 | 10 | 10 |
| Vacation Wanter | 10 | 0  | 0  | 0  | 0  | 0  |

This could potentially equal any request made by others even though it asks much more flexibility of others. (Note in
practice there are rarely meaningful competitive situations - there is almost always a no-lose way to fix due to large
and flexible pool of residents.)

#### Divide by maximum schedulable weeks

We run afoul of integer divisibility immediately - I'll just do traditional rounding, but it does create magic bonus
points
that, strictly speaking, incentivize range requests over singletons. Singleton requests are probably more important to
the resident as well, further complicating the issue.

| Week               | 1            | 2 | 3 | 4 | 5 | 6 |
|--------------------|--------------|---|---|---|---|---|
| ICU Wanter (max 4) | 10/4=2.5 ~ 3 | 3 | 3 | 3 | 3 | 3 |
| Vacation Wanter    | 10           | 0 | 0 | 0 | 0 | 0 |

#### **Divide by request size**

Probably the best and most fair option. Still allows for strategic requests in theory, but again the pool's flexibility
probably makes it unimportant.

| Week               | 1               | 2 | 3 | 4 | 5 | 6 |
|--------------------|-----------------|---|---|---|---|---|
| ICU Wanter (max 4) | 10/6= 1 2/3 ~ 2 | 2 | 2 | 2 | 2 | 2 |
| Vacation Wanter    | 10              | 0 | 0 | 0 | 0 | 0 |

If resident asks for very large range, could get into issues with rounding toward 0. What would that be?