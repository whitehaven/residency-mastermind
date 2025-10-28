# residency-mastermind

Satisfiability solver-driven residency scheduler. Ultimately specific to our local situation, but many parts likely to
be reusable.

## Release Timeline

### target backend usable by end of Nov/early Dec

2026-2027 rotation preferences will be coming in.

#### Remaining missing features

- prerequisite constraints
  - prerequisite logs applied to current
- block-match constraints (must be all in one block or touching border)
- optimization for preferences
- manual forcing of values en bloc
  - alias for rotation-week limitations (like SOM)

## Main Problem

### Decision Variables

- bool for every intersection of Resident, Rotation, and Week

### Constraints

#### By Resident

##### ALl Residents

- 3 weeks vacation must be scheduled for all residents, for all years (except for bonus intern->senior break week)
- All residents should be scheduled on exactly one rotation for a week
- All rotations have an upper limit on simultaneous residents

##### TY

- no existing complete rotations
- must meet requirements
- unclear order of assignments - their program supplies openings, or do we?

##### PMR

- no existing complete rotations
- must meet requirements
- unclear order of assignments - their program supplies openings, or do we?

##### FM Intern

- no existing complete rotations
- must meet requirements
- unclear order of assignments - their program supplies openings, or do we?

##### current IM R1

- no existing completed rotation
- year 1: *primary target* : meet requirements for intern year; note intern->senior break week + vacation(3)
- **year 2**: prove can complete requirements
- **year 3**: prove can complete requirements

##### IM R2

- some completed R1 rotations
- year 1: start on requirements for R2/R3
- **year 2**: complete requirements

##### IM R3

- some completed R1 and R2 rotations
- year 1: complete all requirements for IM program

#### By rotations

- Some rotations require staffing at all times (this is recorded as minimum_residents)
- Some rotations have a certain number of weeks of prerequisite rotations beforehand (can schedule, but must be in
  order)
- Some rotations require that only the interns or senior can change from one week to another to preserve continuity
- Some rotations require assignments to them be contiguous with a minimum length
- Some rotations are only available during specific weeks

#### By Category == Requirement

## Optimization

- [ ] Maximize resident elective preferences
- [ ] Maximize fit of vacation preferences
- [ ] ? get as many rotations done R2 as possible

## Auxiliary tools

- compartmentalized way to force a value to be true arbitrarily (i.e., for setting first-rotation HS or clinic)

## Dev Log

### 2025-08-07

Getting concerned by how complex this problem is.

- some rotations change over time - how can I change a rotation requirement from one year to another? - fortunately only
  this year's requirements matter; old rotations just have to count toward existing requirements
- as above, rotations should generally change on block transition dates to facilitate office work

### 2025-08-08

`9f08d6fa84cca1f5fddbb30f3b20a28f33a747dd` - working do-this-year preference generator for relevant rotations

Test data generator is now working, now for the actual program.

### 2025-08-12

Notably changed vacation blocks to 6 weeks for seniors - in retrospect, not sure how to represent this.

Many single-year constraints implemented and tested. Besides multi-year requirements, still missing:

- HS blocks must start at same times (apparently) - could see if there is flexibility on that from admin

### 2025-08-16

Getting stuck on the multi-year component - it's the only part I don't conceptually have a solution for.

Rewrote constraints - will need to run three years to make things work on the original, though the constraints will be
loosened for year 2 and 3. This just proves all constraints can be completed.

Questions for admin that could cut down (or break open) the sample space:

- are there discrete requirement sets for R2 and R3? Or perhaps the only real set is the entire residency?
- do interns ever do senior rotations?
- who decides when TY/PMR do their IM rotations? Are we just told when they are available?
- how many rotations are offered less than continuously?
- (confirm constraints above)
- do we even care about this project?

### 2025-08-17

Some good progress with breaking up requirement constraints by year.

It seems that maximums of different categories and rotations can be applied for all rotations at the same time. Even so,
it may make sense even to forbid wrong roles from being assigned in the first place. Not sure if it makes more sense
independent of individual roles or just in the respective functions - the fact you're in a function call gives the most
important information. Will plan to place all constraints in the respective function with unified methods external to
those if needed.

### 2025-08-20

Met with admin to positive response. They would like me to schedule the seniors (R2 and R3) since it is a proof of
concept. They even want me to leave all electives as just a placeholder they will work on.

### 2025-08-21

Trialed polars for easier syntax, but the rigidity of the Arrow datatypes means I'd have to dump every single variable
selection `.to_list()` and operate on it. Takes away any benefit. Will revert.

### 2025-08-23

Embarked on conversion to cpmpy to make more modular, understandable, and maintainable code. Wrapping cpmpy array into a
dataframe was easier than expected.

### 2025-08-24

Major progress today with `polars`. The secret was to use `polars` and `cpmpy` together. I could not wrap or-tools
directly, and polars on its own didn't solve the problem of uninterpretable integer indexing in `cpmpy`. Code is much
easier to understand and reason about. Vectorized constraints are seductive but hard.

This is going well enough that I have merged main to this candidate.

### 2025-10-13

Lots of undocumented work done up to this point.

- constraints.py still needs:
    - prerequisite constraint with test, possibly including prerequisites from prior years
    - block alignment for rotations (maybe a type or alternative to existing contiguity code)
    - force selections of variables to True/False (i.e., to specify weeks rotations are offered)

Was trying to use realistic data, but too unwieldy to test situations which require week-perfect scheduling. Adopting a
strategy of creating tight test cases which can only succeed if solved exactly right seems to be a better approach.

