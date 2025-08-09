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

ic(scheduled)

