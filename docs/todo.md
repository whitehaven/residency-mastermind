# To Do List

- [ ] **Import prior completion data**
    - [ ] try digital method from schedules

- [ ] **Rebuild requirements schema and data**
    - [x] Rebuild final schema - now goes rotation >-- category --< requirement, added conditional contiguity
    - [ ] Rebuild data from program's specifications
        - required rotations:
            1. Green and Orange - Rounding HS
                - R3 gets 8 weeks
                - R2 gets 2-4wks (2 have to get 4)
          2. Purple - Admitting HS - R2 only
            3. SHMC ICU
                - 4 weeks for any (subject to preferences)
            4. Night Float
                - 10 (all) R2s get 4wk => R2 Night Float min 4 min contig 4
                - remainder goes to 6 R3s get 1wk and 4 R3s get 2wk => R3 Night Float min 1 max 2, min contig 2 only
                  enforce if 2wk
          5. GIM
                - 4 weeks with minimum and maximum contig 2 (2 x 2wk periods)
          6. Ambulatory Senior
                - R2 gets 4wk
                - R3 gets 4wk
                - Only 1 senior during rotation 1, 2
        - elective rotations (treat as homogenous for testing):
            - Cardiology


- [ ] **Build maximum category constraint from required rotations**


- [ ] **Build maximum and minimum (for Purple) contiguous rotation constraint**
    - [ ] Build testing


- [ ] **Build prerequisites**
    - [ ] Build table
    - [ ] Build constraint
    - [ ] Build testing
    - [ ] Integrate into E2E testing