import itertools as it

import pandas as pd
from icecream import ic
from ortools.sat.python import cp_model

from tools.display import print_full_DataFrame
from tools.optimization import negated_bounded_span

residents = pd.read_csv(
    "testing/residents.csv", index_col=["last_name", "first_name", "degree"]
)
rotations = pd.read_csv("testing/rotations.csv", index_col="rotation")
rotation_categories = pd.read_csv(
    "testing/rotation_categories.csv", index_col="category"
)
preferences = pd.read_csv(
    "testing/preferences.csv",
    index_col=[
        "last_name",
        "first_name",
        "degree",
    ],
)
weeks = pd.read_csv("testing/weeks.csv", index_col="week")

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

# restrict rotations by role

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
