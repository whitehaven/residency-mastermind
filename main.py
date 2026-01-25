import argparse

import box
import cpmpy as cp
import polars as pl

import config
from constraints import (
    enforce_requirement_constraints,
    enforce_rotation_capacity_maximum,
    enforce_rotation_capacity_minimum,
    require_one_rotation_per_resident_per_week,
)
from data_io import generate_pl_wrapped_boolvar, read_bulk_data_sqlite3
from display import convert_melted_to_block_schedule, extract_solved_schedule
from optimization import (
    calculate_total_preference_satisfaction,
    create_preference_objective,
)


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

    # Load preferences if provided
    preferences = None
    if args.preferences:
        preferences = pl.read_csv(args.preferences)
        # Ensure week column is properly formatted
        if "week" in preferences.columns and preferences["week"].dtype == pl.Utf8:
            preferences = preferences.with_columns(pl.col("week").str.to_datetime())

    solved_schedule = solve_schedule(
        residents,
        rotations,
        weeks_this_acad_year,
        preferences=preferences,
        optimize=args.optimize,
    )

    return solved_schedule


def solve_schedule(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    preferences: pl.DataFrame | None = None,
    optimize: bool = False,
) -> pl.DataFrame:
    """
    Solve schedule as represented by residents, rotations, and weeks.

    This should handle all filtering before dispatching for efficiency.

    Args:
        residents: DataFrame of residents
        rotations: DataFrame of rotations
        weeks: DataFrame of weeks
        preferences: Optional DataFrame with preference scores
        optimize: Whether to optimize for preferences or just find feasible solution

    Returns:
        scheduled: pl.DataFrame containing the cartesian product of residents, rotations, and weeks along with cpmpy variables and their results
    """
    model = cp.Model()

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)

    # TODO Constraints
    # resident-specific

    current_requirements = box.box_from_file(config.DEFAULT_REQUIREMENTS_PATH)
    if not isinstance(current_requirements, box.Box):
        raise TypeError

    # Create empty prior rotations for now
    prior_rotations_completed = pl.DataFrame(
        {"resident": [], "rotation": [], "completed_weeks": []}
    )

    model += enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
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

    # Optimization
    if optimize and preferences is not None:
        objective = create_preference_objective(scheduled, preferences)
        model.maximize(objective)

        is_optimal = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=True)
        if not is_optimal:
            raise ValueError("No optimal solution found")

        solved_schedule = extract_solved_schedule(scheduled)
        total_satisfaction = calculate_total_preference_satisfaction(
            solved_schedule, preferences
        )
        print(f"Total preference satisfaction: {total_satisfaction}")
    else:
        # Solve model (feasibility only)
        is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=True)
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
    parser.add_argument(
        "-o",
        "--optimize",
        action="store_true",
        help="optimize for preference satisfaction instead of just feasibility",
        required=False,
    )
    parser.add_argument(
        "-p",
        "--preferences",
        type=str,
        help="CSV file with resident preferences (resident, rotation, week, preference)",
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
