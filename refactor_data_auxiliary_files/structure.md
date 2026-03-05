# structure plan

## residents.csv
name | year | track | modifier

## weeks.csv
monday_date | ?week_num | ?block

## rotations.yaml: 

- [ ] overriding inheritance?

- Mandatory:
  - name
  - min residents
  - max residents
- Optional:
  - Available weeks ^ Unavailable weeks
  - ?Request-only (?subtractive modifier)

## requirements <= submodules*.yaml

- [ ] overwriting inheritance? or is that too confusing?

- Mandatory:
  - name
  - fulfilled_by: `[rotation_n...]`
- Optional:
  - min weeks
  - max weeks
  - min contig
  - max contig
  - must_align_to_block
  - ?prereq (vs in rotations.yaml)