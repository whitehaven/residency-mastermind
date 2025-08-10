import itertools as it

import pandas as pd
from icecream import ic
from ortools.sat.python import cp_model

import data_handler
from optimization import negated_bounded_span
from tools.display import print_full_DataFrame

residents, rotations, rotation_categories, preferences, weeks = data_handler.read_data()

model = cp_model.CpModel()
model.SetName("Resident Scheduler")

scheduled = model.NewBoolVarSeries(
    "is_scheduled_",
    pd.Index((list(it.product(residents.index, rotations.index, weeks.index)))),
).sort_index()

# TODO Constraints
# every resident's week x must have exactly 1 scheduled rotation or vacation (which is a "rotation")
for resident, week in it.product(residents.index, weeks.index):
    model.AddExactlyOne(scheduled.loc[pd.IndexSlice[resident, :, week]])

# >>> restrict rotations by role

# join rotation to rotation_categories since these are recorded in the rotation_categories table
rotations_with_categories = pd.merge(
    rotations,
    rotation_categories,
    left_on="category",
    right_index=True,
    how="inner",
    suffixes=("_rotations", "_categories"),
)

# for seniors: set non-senior roles to False (note "Any" left in)
for resident, rotation in it.product(
    residents.loc[(residents.role == "IM-Senior")].index,
    rotations_with_categories.loc[
        ~((rotations_with_categories.pertinent_role.isin(["Senior", "Any"])))
    ].index,
):
    for week in weeks.index:
        model.Add(scheduled.loc[(resident, rotation, week)] == False)

# for im interns: set non intern + im intern roles to false
for resident, rotation in it.product(
    residents.loc[residents.role == "IM-Intern"].index,
    rotations_with_categories.loc[
        ~(
            rotations_with_categories.pertinent_role.isin(
                ["Any Intern", "IM Intern", "Any"]
            )
        )
    ].index,
):
    for week in weeks.index:
        model.Add(scheduled.loc[(resident, rotation, week)] == False)


# for TY interns, set non-TY intern roles to false
for resident, rotation in it.product(
    residents.loc[residents.role.isin(["TY"])].index,
    rotations_with_categories.loc[
        ~(
            rotations_with_categories.pertinent_role.isin(
                ["Any Intern", "TY_Intern", "Any"]
            )
        )
    ].index,
):
    for week in weeks.index:
        model.Add(scheduled.loc[(resident, rotation, week)] == False)

# for PMR interns: set non- PMR roles to false
for resident, rotation in it.product(
    residents.loc[residents.role.isin(["PMR"])].index,
    rotations_with_categories.loc[
        ~(
            rotations_with_categories.pertinent_role.isin(
                ["Any Intern", "PMR Intern", "Any"]
            )
        )
    ].index,
):
    for week in weeks.index:
        model.Add(scheduled.loc[(resident, rotation, week)] == False)

# set minimum number of residents scheduled for rotations that require that
for rotation_head, rotation_tail in rotations.iterrows():
    if rotation_tail["minimum_residents_assigned"] > 0:
        for week in weeks.index:
            model.Add(
                sum(scheduled.loc[pd.IndexSlice[:, rotation_head, week]])  # type: ignore
                >= rotation_tail["minimum_residents_assigned"]
            )

# minimum contiguous weeks for rotations that require that
for rotation_head, rotation_tail in rotations.iterrows():
    if rotation_tail["minimum_contiguous_weeks"] > 1:
        for resident in residents.index:
            hard_minimum = rotation_tail.minimum_contiguous_weeks
            sequence = scheduled.loc[
                pd.IndexSlice[resident, rotation_head, :]  # type:ignore
            ]  # TODO: test
            for length in range(1, hard_minimum):
                for start in range(len(sequence) - length + 1):
                    model.AddBoolOr(negated_bounded_span(sequence, start, length))

# limit total weeks for each resident in each rotation with specific limits
for resident_head, resident_tail in residents.iterrows():
    for rotation_head, rotation_tail in rotations.loc[
        rotations.maximum_weeks.notna()
    ].iterrows():
        model.Add(
            sum(scheduled.loc[pd.IndexSlice[resident_head, rotation_head, :]])  # type: ignore
            <= int(rotation_tail.maximum_weeks)
        )

# limit total weeks for each resident in each rotation category that has its own limits
for resident_head, resident_tail in residents.iterrows():
    for (
        rotation_with_categories_head,
        rotation_with_categories_tail,
    ) in rotations_with_categories.loc[
        rotations_with_categories.maximum_weeks_categories.notna()
    ].iterrows():
        model.Add(
            sum(
                scheduled.loc[
                    pd.IndexSlice[resident_head, rotation_with_categories_head, :]  # type: ignore
                ]
            )
            <= int(rotation_with_categories_tail.maximum_weeks_categories)
        )

# TODO Optimization targets

ic(model.ModelStats())

# solve model
solver = cp_model.CpSolver()
solver.parameters.log_search_progress = True
solver.log_callback = print
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print("optimal")
    print("=====Stats:======")
    print(solver.SolutionInfo())
    print(solver.ResponseStats())
elif status == cp_model.FEASIBLE:
    print("feasible")
    print("=====Stats:======")
    print(solver.SolutionInfo())
    print(solver.ResponseStats())
else:
    print("no solution")

print_full_DataFrame(
    solver.Values(scheduled)[solver.Values(scheduled) == 1]
    .sort_index(level=(0, 2))
    .unstack()
    .reset_index()
    .melt(id_vars=["level_0", "level_1"])
    .query("value == 1")
    .set_index(["level_0", "variable"])
    .sort_index()["level_1"]
    .unstack()
)
