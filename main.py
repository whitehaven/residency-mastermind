import argparse

import box
import cpmpy as cp
import polars as pl

from constraints import (
    enforce_rotation_capacity_maximum,
    require_one_rotation_per_resident_per_week,
    enforce_rotation_capacity_minimum,
    enforce_minimum_contiguity,
    enforce_requirement_constraints,
)
from data_io import (
    read_bulk_data_sqlite3,
    generate_pl_wrapped_boolvar,
)
from display import (
    extract_solved_schedule,
    convert_melted_to_block_schedule,
)

config = box.box_from_file("config.yaml")


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

    # TODO handle R3-extended (just filtered out immediately here)
    standard_scheduled_residents = residents.filter(pl.col("year").is_in(["R2", "R3"]))

    scheduled = generate_pl_wrapped_boolvar(
        standard_scheduled_residents, rotations, weeks
    )

    # TODO Constraints
    # resident-specific

    current_requirements = box.box_from_file(config.default_requirements_path)

    model += enforce_requirement_constraints(
        current_requirements, standard_scheduled_residents, rotations, weeks, scheduled
    )

    model += require_one_rotation_per_resident_per_week(
        standard_scheduled_residents, rotations, weeks, scheduled
    )

    rotations_with_min_contiguity_reqs = rotations.filter(
        (pl.col("minimum_contiguous_weeks") > 1)
        & (pl.col("minimum_contiguous_weeks").is_not_null())
    )
    model += enforce_minimum_contiguity(
        standard_scheduled_residents,
        rotations_with_min_contiguity_reqs,
        weeks,
        scheduled,
    )

    # rotation-specific (to physical site, not requirement)
    rotations_with_capacity_minimum = rotations.filter(
        pl.col("minimum_residents_assigned") > 0
    )
    model += enforce_rotation_capacity_minimum(
        standard_scheduled_residents, rotations_with_capacity_minimum, weeks, scheduled
    )

    rotations_with_capacity_maximum = rotations.filter(
        pl.col("maximum_residents_assigned").is_not_null()
    )
    model += enforce_rotation_capacity_maximum(
        standard_scheduled_residents, rotations_with_capacity_maximum, weeks, scheduled
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
