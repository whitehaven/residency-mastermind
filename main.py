import argparse

import cpmpy as cp
import polars as pl

from constraints import (
    enforce_rotation_capacity_maximum,
    require_one_rotation_per_resident_per_week,
    enforce_rotation_capacity_minimum,
    enforce_minimum_contiguity,
)
from data_io import (
    read_bulk_data_sqlite3,
    generate_pl_wrapped_boolvar,
)
from display import (
    extract_solved_schedule,
    convert_melted_to_block_schedule,
)


def main(args_from_commandline=None, read_db: str | None = None) -> pl.DataFrame:
    if args_from_commandline is None:
        db_location = read_db
    elif read_db is None:
        db_location = args_from_commandline.database
    else:
        assert False, "No input db specified"

    input_tables = read_bulk_data_sqlite3(db_location)

    residents = input_tables["residents"]
    rotations = input_tables["rotations"]
    weeks = input_tables["weeks"]

    current_academic_starting_year = 2025
    weeks_this_acad_year = weeks.filter(
        pl.col("starting_academic_year") == current_academic_starting_year  # type: ignore
    )

    standard_scheduled_residents = residents.filter(pl.col("year").is_in(["R2", "R3"]))

    scheduled = solve_schedule(
        standard_scheduled_residents, rotations, weeks_this_acad_year
    )

    solved_schedule = extract_solved_schedule(scheduled)

    return solved_schedule


def solve_schedule(residents, rotations, weeks):
    model = cp.Model()
    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)

    # TODO Constraints
    # resident-specific
    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    # Requirement-specific

    rotations_with_min_contiguity_reqs = rotations.filter(
        (pl.col("minimum_contiguous_weeks") > 1)
    )
    model += enforce_minimum_contiguity(
        residents, rotations_with_min_contiguity_reqs, weeks, scheduled
    )

    # model += enforce_requirement_constraints(residents, rotations, weeks, scheduled)

    # rotation-specific
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)

    # enforce block transitions

    # category-specific
    # enforce maximum

    # TODO Optimization
    # maximize rotation preferences + vacation preferences (? + completion of 2nd year rotations if possible)
    # Solve model
    is_feasible = model.solve("ortools", log_search_progress=True)
    if not is_feasible:
        raise ValueError("Infeasible")
    return scheduled


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Residency Mastermind",
        description="Constraint-based residency scheduling program",
        epilog="Alex Conrad Crist, DO",
    )
    parser.add_argument(
        "-d",
        "--database",
        type=str,
        help="sqlite3 database file",
        required=True,
    )
    parser.add_argument(
        "-b",
        "--block-output",
        type=str,
        help="output block schedule",
        required=False,
    )
    args = parser.parse_args()

    melted_solved_schedule = main(args)
    block_schedule = convert_melted_to_block_schedule(melted_solved_schedule)

    if args.block_output:
        block_schedule.write_csv(args.block_output)
        print(f"wrote block schedule to {args.block_output}")
    else:
        print(block_schedule)
