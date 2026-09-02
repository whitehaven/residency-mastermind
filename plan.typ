#set heading(numbering: "1.1.")
#import "@preview/dashy-todo:0.1.3": todo

= Read/Generate Inputs
== Workers <workers>
Workers are 1:1 records. Internal data is `polars.Dataframe`.

#figure(
  table(
    columns: 3,
    table.header[name][year][track],
    [Doctor A], [R2], [Standard],
    [Doctor B], [R3], [PCT],
  ),
  caption: [Workers, table formulation],
)

=== Validation
- no exact name repeats
- year and track must be members of allowed years and tracks #todo()[but then where get this?]

== Rotations <rotations>
Rotations are key:value records representing physical locations. Internal data is key:value pairs. #todo()[currently is
  tabular, need implementing]

#figure(
  [
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
  ],
  caption: [Rotations yaml formulation],
)

=== Validation

- datatypes must match (i.e., `min_residents` must be `int`)
- `min_residents <= max_residents`; `min_*` must be below `max_*`, etc.
- no overlap of available/unavailable weeks

== Weeks <weeks>

Manually generated each year - too many particularities with academic years to determine programatically.

By far the simplest of the inputs. Simple tabular 1:1 data. Internal form is `polars.DataFrame`.

#figure(
  table(
    columns: 3,
    table.header[monday_date][week][block],
    [2026-07-06], [1], [1],
    [2026-07-13], [2], [1],
    [2026-07-20], [3], [1],
    [2026-07-27], [4], [1],
  ),
  caption: [Weeks, table formulation],
)

== Requirement sets <requirements>
Each resident has characteristics that determine their needs. #todo()[joins to find all group types?]

In our case these are resident years and tracks, so not terribly complicated. #todo()[Does it make more sense to iterate
  by worker? or by requirement set?]

#figure(
  ```yaml
    HS Admitting Senior:
    constraints:
      max_by_period: 6
      min_by_period: 5
      min_contiguity: 2
    fulfilled_by: Purple HS Senior
  HS Rounding Senior:
    constraints:
      max_by_period: 4
      max_contiguity: 4
      min_by_period: 2
      min_contiguity: 2
      prerequisites:
        prerequisite_fulfillers:
        - Purple HS Senior
        prerequisite_weeks: 2
      respect_block_alignment: true
    fulfilled_by:
    - Green HS Senior
    - Orange HS Senior
  ```,
  caption: [Requirements yaml formulation],
)

=== Requirement set composition

Using `mergedeep` python library, individual sets of requirements are generated for all distinct worker groups.

The general structure is
$ "Year" union "Track" union "Special Circumstances" $

Requirements are superceded from general to specific; e.g., if an R2 needs 8 weeks clinic and is on Primary Care Track,
this is raised to 12 weeks. The Primary Care Track set of requirements supercedes the base R2 set.

Note there is no (good) way to fully delete requirements by supercession - all residents are treated as having a track,
i.e., an R2 planning on being a hospitalist is given the "Standard" track. #footnote()[In theory, the requirement's `min_weeks` parameters could be set to 0 in supercession, effectively deleting the requirement. This is hideous, however, and should be avoided.]

#todo()[Complete set composition code]

== Scheduled variables blocks
Created from cartesian product (`pl.DataFrame.join(how="cross,...`) of Workers, Rotations and Weeks.

Internally `polars.DataFrame` that is created at runtime.

#figure(
  table(
    columns: 4,
    table.header[worker cols ...][rotation cols...][week cols...][is_scheduled],
    [Doctor A ...], [Green HS Senior ...], [2026-07-06 ...], [boolvar@(Doctor A, Green HS Senior, 2026-07-06)],
  ),
  caption: [scheduled, table form],
)

== Overrides <overrides>
#figure(
  table(
    columns: 5,
    table.header[worker][rotation][week (`monday_date`)][overriding_value][comment],
    [Doctor A], [Vacation], [2026-07-27], [True], [previously granted vacation],
  ),
  caption: [weeksf, table form],
)

=== Validation

- `resident`, `rotation`, `week` ∈ respective sets
- `overriding_value` ∈ boolean
- Error on duplicates of `resident` & `rotation` & `week`

== Requests <requests>
#figure(
  table(
    columns: 6,
    table.header[worker][rotation][start week (`monday_date`)][end week (`monday date`)][request polarity][priority],
    [Resident A], [Elective], [2026-07-06], [2026-07-27], [preference], [high],
    [Resident B], [SHMC ICU Senior], [2026-09-14], [2026-10-05], [avoidance], [high],
  ),
  caption: [requests, table form],
)

=== Validation

- `resident`, `rotation`, `week_start`,`week_end` ∈ respective sets
- `request_polarity` ∈ preference/positive | avoidance/negative
- `priority` ∈ high/medium/low
- when `week_start` and `week_end` are equal, optimality bonus/penalty is applied
- when `week_start` and `week_end` are not equal, unclear what to do with bonus/penalty - probably would divide over
  minimum size of rotation - see below.

==== Handling of multi-week bonus/penalty

The primary issue is of fairness between residents - if the same penalty or bonus was applied in a multi-week case, this
would advantage that resident because multiple weeks will stack.

For example, if we were trying to incentivize placing a person on ICU early while someone else asks for vacation. We'll
say weeks 1-6 are "early".

===== Naive

#table(
  columns: 7,
  table.header[Week][1][2][3][4][5][6],
  [ICU Wanter], [10], [10], [10], [10], [10], [10],
  [Vacation Wanter], [10], [0], [0], [0], [0], [0],
)

This could potentially equal any request made by others even though it asks much more flexibility of others. (Note in
practice there are rarely meaningful competitive situations - there is almost always a no-lose way to fix due to large
and flexible pool of residents.)

===== Divide by maximum schedulable weeks

We run afoul of integer divisibility immediately - I'll just do traditional rounding, but it does create magic bonus
points that, strictly speaking, incentivize range requests over singletons. Singleton requests are probably more
important to the resident as well, further complicating the issue.

Resident below can ask for 4 weeks, so their "pull" to ask for them could be divided by their needs, like below:

#table(
  columns: 7,
  table.header[Week][1][2][3][4][5][6],
  [ICU Wanter (max4 4)], [$10/4 = 2.5 ≈ 3$], [3], [3], [3], [3], [3],
  [Vacation Wanter], [10], [0], [0], [0], [0], [0],
)
===== Divide by request size

Probably the best and most fair option. Still allows for strategic requests in theory, but again the pool's flexibility
probably makes it unimportant.

#table(
  columns: 7,
  table.header[Week][1][2][3][4][5][6],
  [ICU Wanter (max4 4)], [$10 / 6 = 1 2/3 ≈ 2$], [2], [2], [2], [2], [2],
  [Vacation Wanter], [10], [0], [0], [0], [0], [0],
)
If resident asks for very large range, could get into issues with rounding toward 0.

= Input Validation
Check

= Constraint Generation
Process each logical group, generating the `cpmpy` expressions to express all constraints.

$forall$

= Optimization Function Generation

= Solve Model

= Error/Failure Handling
Using `cpmpy.tools.MUS`, we can generate a minimum unsolvable set of constraints - this can be hard to trace back to the
originating constraint, but can help diagnose contradictory constraints.

= Versioning
See `pyproject.toml`.

#outline(title: "TODOs", target: figure.where(kind: "todo"))

