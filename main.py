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
    create_preferences_objective,
)


def main(args):
    raise NotImplementedError("Put primary run here. Will need interface built.")


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
