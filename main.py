import itertools as it

import pandas as pd
from ortools.sat.python import cp_model

from constraints import (
    enforce_minimum_contiguity,
    set_IM_R1_constraints,
    set_single_year_resident_constraints,
)
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

    set_IM_R1_constraints(
        residents,
        rotations,
        weeks,
        categories,
        model,
        scheduled,
        starting_academic_year=2025,
    )

    # Rotation-wise constraints

    enforce_minimum_contiguity(residents, rotations, model, scheduled, weeks)

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
        solver.Values(scheduled)
        .unstack()
        .reset_index()
        .rename({"level_0": "resident", "level_1": "rotation"}, axis="columns")
        .melt(id_vars=["resident", "rotation"], var_name="date")
        .query("value == 1")
        .set_index(["resident", "date"])
    )

    print(consolidated_schedule)
    # print_full_dataframe(consolidated_schedule)


if __name__ == "__main__":
    main()
