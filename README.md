# residency-mastermind

Satisfiability solver-driven residency scheduler. Ultimately specific to our local situation, but many parts likely to be reusable.

## Core Functionality

- compartmentalized way to force a value to be true arbitrarily (i.e., for setting first-rotation HS or clinic)

## Variables

- bool for every intersection of Resident, Rotation, and Week

## Constraints

### For all Residents

- [ ] Each resident must be scheduled on a rotation or vacation
- [ ] All new interns start in clinic or HS, then HS or clinic respectively

### For all Rotations

- [ ] resident only added if they can fit the prescribed number of weeks `min_contig_wks`
- [ ] No fewer resients than required (i.e., the HS services must be fully staffed)
- [ ] No more residents per week than `resident capacity`
- [ ] Rotations that require intern or senior are restricted by role
- [ ] Some rotations can only change personel on 1-block division to facilitate notification of preceptors. (HS must match blocks).
- [ ] Some rotations can't have all team members change simultaneously (seemingly only ICU and Rounding HS, (as DH no longer has senior position))

### For all Categories

- [ ] Residents can't exceed a certain number of rotation types, i.e., <6 months in any ICU context

## Optimization targets

- [ ] Maximize resident elective preferences
- [ ] Maximize fit of vacation preferences (perhaps vacation could be a special rotation that must be done 3 weeks a year?)

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

Questions for admin that could cut down (or break open) the sample space:

- are there discrete requirement sets for R2 and R3? Or perhaps the only real set is the entire residency?
- who decides when TY/PMR do their IM rotations? Are we just told when they are available?
- how many rotations are offered less than continuously?
- (confirm contraints above)
- do we even care about this project?