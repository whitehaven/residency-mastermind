import cpmpy as cp
import polars as pl

from constraints import (
    require_one_rotation_per_resident_per_week,
    enforce_rotation_capacity_ranges,
)
from data_io import (
    read_bulk_data_sqlite3,
    generate_pl_wrapped_boolvar,
)
from display import extract_solved_schedule


def main():
    input_tables = read_bulk_data_sqlite3("seniors_only.db")

    residents = input_tables["residents"]
    rotations = input_tables["rotations"]
    categories = input_tables["categories"]
    preferences = input_tables["preferences"]
    weeks = input_tables["weeks"]
    rotations_completed = input_tables["rotations_completed"]

    current_academic_starting_year = 2025

    weeks_this_acad_year = weeks.filter(
        pl.col("starting_academic_year") == current_academic_starting_year
    )

    model = cp.Model()

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)

    # TODO Constraints

    # resident-specific
    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks_this_acad_year, scheduled
    )

    # rotation-specific
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    # TODO Optimization

    # TODO Solve model

    is_feasible = model.solve("ortools", log_search_progress=True)
    if not is_feasible:
        raise ValueError("Infeasible")

    # TODO Visualize
    solved_schedule = extract_solved_schedule(scheduled)
    print(solved_schedule)


if __name__ == "__main__":
    main()
