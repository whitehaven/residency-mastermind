import argparse

import box
import cpmpy as cp
import polars as pl

from config import config
from constraints import (
    enforce_requirement_constraints,
    enforce_rotation_capacity_maximum,
    enforce_rotation_capacity_minimum,
    require_one_rotation_per_resident_per_week,
)
from data_io import generate_pl_wrapped_boolvar, read_bulk_data_sqlite3
from display import convert_melted_to_block_schedule, extract_solved_schedule


def main(args_from_commandline=None) -> pl.DataFrame:
    if args_from_commandline is None:
        raise ValueError("No db specified")
    db_location = args_from_commandline.database

    input_tables = read_bulk_data_sqlite3(db_location)

    residents = input_tables["residents"]
    rotations = input_tables["rotations"]
    weeks = input_tables["weeks"]

    current_academic_starting_year = 2025
    weeks_this_acad_year = weeks.filter(
        pl.col("starting_academic_year") == current_academic_starting_year  # type: ignore
    )

    solved_schedule = solve_schedule(residents, rotations, weeks_this_acad_year)

    return solved_schedule


def solve_schedule(
    residents: pl.DataFrame, rotations: pl.DataFrame, weeks: pl.DataFrame
) -> pl.DataFrame:
    """
    Solve schedule as represented by residents, rotations, and weeks.

    This should handle all filtering before dispatching for efficiency.

    Returns:
        scheduled: pl.DataFrame containing the cartesian product of residents, rotations, and weeks along with cpmpy variables and their results
    """
    model = cp.Model()

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)

    # TODO Constraints
    # resident-specific

    current_requirements = box.box_from_file(config.default_requirements_path)
    if not isinstance(current_requirements, box.Box):
        raise TypeError

    model += enforce_requirement_constraints(
        current_requirements, residents, rotations, weeks, scheduled
    )

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )

    # rotation-specific (to physical site, not requirement)
    rotations_with_capacity_minimum = rotations.filter(
        pl.col("minimum_residents_assigned") > 0
    )
    model += enforce_rotation_capacity_minimum(
        residents, rotations_with_capacity_minimum, weeks, scheduled
    )

    rotations_with_capacity_maximum = rotations.filter(
        pl.col("maximum_residents_assigned").is_not_null()
    )
    model += enforce_rotation_capacity_maximum(
        residents, rotations_with_capacity_maximum, weeks, scheduled
    )

    # TODO enforce block transitions

    # TODO Optimization
    # maximize rotation preferences + vacation preferences (? + completion of 2nd year rotations if possible)
    # Solve model
    is_feasible = model.solve("ortools", log_search_progress=True)
    if not is_feasible:
        raise ValueError("Infeasible")

    solved_schedule = extract_solved_schedule(scheduled)

    return solved_schedule


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
