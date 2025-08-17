# residency-mastermind

Satisfiability solver-driven residency scheduler. Ultimately specific to our local situation, but many parts likely to be reusable.

## Core Functionality

- compartmentalized way to force a value to be true arbitrarily (i.e., for setting first-rotation HS or clinic)

## Variables

- bool for every intersection of Resident, Rotation, and Week

## Constraints

### TY

- no existing complete rotations
- must meet
- unclear order of assignments - their program supplies openings, or do we?

### PMR

- no existing complete rotations
- must meet
- unclear order of assignments - their program supplies openings, or do we?

### current IM R1

- no existing completed rotation
- year 1: *primary target* : meet requirements for intern year; note intern->senior break week + vacation(3)
- **year 2**: prove can complete requirements
- **year 3**: prove can complete requirements

### IM R2

- some completed R1 rotations
- year 1: start on requirements for R2/R3
- **year 2**: complete requirements

### IM R3

- some completed R1 and R2 rotations
- year 1: complete all requirements for IM program

# Apply to all:

- All residents should be scheduled on exactly one rotation for a week
- All rotations have an upper limit on simultaneous residents
- Some rotations require staffing at all times (this is recorded as minimum_residents)
- Some rotations have a certain number of weeks of prerequisite rotations beforehand (can schedule, but must be in
  order)
- Some rotations require that only the interns or senior can change from one week to another to preserve continuity
- Some rotations require assignments to them be contiguous with a minimum length
- Some rotations are only available during specific weeks
- 3 weeks vacation must be scheduled for all residents, for all years (except for bonus intern->senior break week)

## Optimization targets

- [ ] Maximize resident elective preferences
- [ ] Maximize fit of vacation preferences

## Dev Log

### 2025-08-07

Getting concerned by how complex this problem is.

- some rotations change over time - how can I change a rotation requirement from one year to another? - fortunately only this year's requirements matter; old rotations just have to count toward existing requirments
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
- who decides when TY/PMR do their IM rotations? Are we just told when they are available?
- how many rotations are offered less than continuously?
- (confirm constraints above)
- do we even care about this project?