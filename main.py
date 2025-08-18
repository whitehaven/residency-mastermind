import itertools as it

import pandas as pd
from ortools.sat.python import cp_model

from constraints import set_single_year_resident_constraints, set_im_r1_constraints
from data_io import read_data_sqlite3
from display import print_full_dataframe


def main():
    input_tables = read_data_sqlite3("residency_mastermind.db")

    residents = input_tables["residents"]
    rotations = input_tables["rotations"]
    categories = input_tables["categories"]
    preferences = input_tables["preferences"]
    weeks = input_tables["weeks"]

    model = cp_model.CpModel()
    model.SetName("Resident Scheduler")

    scheduled = model.NewBoolVarSeries(
        "is_scheduled_",
        pd.Index(
            (
                list(
                    it.product(
                        residents.full_name, rotations.rotation, weeks.monday_date
                    )
                )
            )
        ),
    ).sort_index()

    set_single_year_resident_constraints(
        "PMR",
        residents,
        rotations,
        weeks,
        categories,
        model,
        scheduled,
        starting_academic_year=2025,
    )
    set_single_year_resident_constraints(
        "TY",
        residents,
        rotations,
        weeks,
        categories,
        model,
        scheduled,
        starting_academic_year=2025,
    )

    # Optimization

    # solve model
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = True
    solver.log_callback = print
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        print("no solution")
        return
    elif status == cp_model.OPTIMAL:
        print("optimal")
        print("=====Stats:======")
    elif status == cp_model.FEASIBLE:
        print("feasible")
        print("=====Stats:======")
    else:
        print("undefined error")
        return

    print(solver.SolutionInfo())
    print(solver.ResponseStats())

    consolidated_schedule = (
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

    print_full_dataframe(consolidated_schedule)


if __name__ == "__main__":
    main()
