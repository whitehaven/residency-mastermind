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
