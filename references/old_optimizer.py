import itertools as it

import pandas as pd
from ortools.sat.python import cp_model


def negated_bounded_span(works, start, length):
    """Filters an isolated sub-sequence of variables assigned to True.

    Extract the span of Boolean variables [start, start + length), negate them,
    and if there is variables to the left/right of this span, surround the span by
    them in non negated form.

    Args:
      works: a list of variables to extract the span from.
      start: the start to the span.
      length: the length of the span.

    Returns:
      a list of variables which conjunction will be false if the sub-list is
      assigned to True, and correctly bounded by variables assigned to False,
      or by the start or end of works.
    """
    sequence = []
    # left border (start of works, or works[start - 1])
    if start > 0:
        sequence.append(works[start - 1])
    for i in range(length):
        sequence.append(~works[start + i])
    # right border (end of works or works[start + length])
    if start + length < len(works):
        sequence.append(works[start + length])
    return sequence


def read_entire_sqlite_blind(dbfile):
    """
    Reads all tables from a SQLite database file into a dictionary of DataFrames.
    Source: https://stackoverflow.com/questions/36028759/how-to-open-and-convert-sqlite-database-to-pandas-dataframe
    """
    import sqlite3

    from pandas import read_sql_query, read_sql_table

    with sqlite3.connect(dbfile) as dbcon:
        tables = list(
            read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", dbcon)[
                "name"
            ]
        )
        out = {
            tbl: read_sql_query(f"SELECT * from {tbl}", dbcon) for tbl in tables
        }  # maybe this was supposed to be read_sql_table?

    return out


def print_full_DataFrame(df):
    """
    Prints a DataFrame in full, overriding truncation, then resets the option.
    Source: https://stackoverflow.com/questions/2058552/how-to-print-a-pandas-data
    """
    import pandas as pd

    pd.set_option("display.max_rows", len(df))
    print(df)
    pd.reset_option("display.max_rows")
    return None


MAX_WKS = 52

prefs = pd.read_csv(
    "resident_scheduling_input/preferences.csv", index_col="resident_name"
)
rotations = pd.read_csv(
    "resident_scheduling_input/rotations.csv", index_col="rotation_name"
)
residents = pd.read_csv(
    "resident_scheduling_input/residents.csv", index_col="resident_name"
)
weeks = pd.read_csv("resident_scheduling_input/weeks.csv", index_col="week_n")
categories = pd.read_csv(
    "resident_scheduling_input/categories.csv", index_col="category"
)

model = cp_model.CpModel()

d = model.NewBoolVarSeries(
    "bool_at_",
    pd.Index((list(it.product(residents.index, rotations.index, weeks.index)))),
).sort_index()  # makes a dummy pd.Series with strings that are labels

# every resident's week x must have exactly 1 rotation (has not had vacations incorporated)
for n, w in it.product(residents.index, weeks.index):
    model.AddExactlyOne(d.loc[pd.IndexSlice[n, :, w]])

# # TODO apply max capacity to each rotation for each rotation:week index, probably requires splaying all residents over their entire residency
# for r, w in it.product(rotations.index, weeks.index):
#     model.Add(sum(d.loc[pd.IndexSlice[:, r, w]]) <= rotations.resident_capacity[r])

# for each rotation, set max weeks to use
for rot_name, rot_tail in rotations.iterrows():
    for res in residents.index:
        if rot_tail["max_wks"] <= MAX_WKS:  # may be
            model.Add(
                sum(d.loc[pd.IndexSlice[res, rot_name, :]]) <= rot_tail["max_wks"]
            )

# # TODO set senior requirements - can't run because requires splaying all residents over their entire residency
# for rot_name, rot_tail in rotations[(rotations.min_wks > 0) & (rotations.required_level == "Senior")].iterrows():
#     for res in residents[residents.resident_year > 1].index:
#         model.Add(sum(d.loc[pd.IndexSlice[res, rot_name, :]]) >= rot_tail.min_wks)

# # TODO set intern requirements - can't run because requires splaying all residents over their entire residency
# for rot_name, rot_tail in rotations[(rotations.min_wks > 0) & (rotations.required_level == "Intern")].iterrows():
#     for res in residents[residents.resident_year == 1].index:
#         model.Add(sum(d.loc[pd.IndexSlice[res, rot_name, :]]) >= rot_tail.min_wks)

# for any rotations which require contiguous weeks
rotations_with_contig_reqs = rotations[rotations.min_contig_wks > 1]
for contig_rot, contig_rot_tail in rotations_with_contig_reqs.iterrows():
    for res in residents.index:
        hard_min = contig_rot_tail.min_contig_wks
        sequence = d.loc[pd.IndexSlice[res, contig_rot, :]]
        for length in range(1, hard_min):
            for start in range(len(sequence) - length + 1):
                model.AddBoolOr(negated_bounded_span(sequence, start, length))

# TODO vacations - not implemented yet

# TODO make Maximization objective function
# model.Maximize(
#     sum(
#         [
#             d.loc[pd.IndexSlice[res, rot, wk]] * prefs.loc[res, rot]
#             for res in residents.index
#             for rot in rotations.index
#             for wk in weeks.index
#         ]
#     )
# )


model.SetName("Resident Scheduler")
print(model.ModelStats())


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

utils.data_handling.print_full_DataFrame(
    solver.Values(d)[solver.Values(d) == 1]
    .sort_index(level=(0, 2))
    .unstack()
    .reset_index()
    .melt(id_vars=["level_0", "level_1"])
    .query("value == 1")
    .set_index(["level_0", "variable"])
    .sort_index()["level_1"]
    .unstack()
)
