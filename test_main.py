import warnings

import box
import polars as pl
import pytest

import config
from display import convert_melted_to_block_schedule, extract_solved_schedule
from main import solve_schedule
from test_constraints import (
    verify_enforce_requirement_constraints,
    verify_enforce_rotation_capacity_maximum,
    verify_enforce_rotation_capacity_minimum,
    verify_one_rotation_per_resident_per_week,
)

test_residents_path = config.TESTING_FILES["residents"]["real_size_seniors"]
test_rotations_path = config.TESTING_FILES["rotations"]["real_size"]
test_weeks_path = config.TESTING_FILES["weeks"]["full_academic_year_2025_2026"]

@pytest.mark.skip(
    reason="duplicates function of constraint tests at this point, only needed when optimization also implemented"
)
def test_solve_schedule():
    residents = pl.read_csv(test_residents_path)
    rotations = pl.read_csv(test_rotations_path)
    weeks = pl.read_csv(test_weeks_path, try_parse_dates=True)

    residents = residents.filter(pl.col("year").is_in(["R2"]))
    warnings.warn("NOTE: Filtering to R2 only ")

    current_requirements = box.box_from_file(config.DEFAULT_REQUIREMENTS_PATH)
    if not isinstance(current_requirements, box.Box):
        raise TypeError

    scheduled = solve_schedule(residents, rotations, weeks)

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_one_rotation_per_resident_per_week(
        melted_solved_schedule,
    ), "verify_one_rotation_per_resident_per_week failed"
    assert verify_enforce_rotation_capacity_minimum(
        rotations,
        melted_solved_schedule,
    ), "verify_enforce_rotation_capacity_minimum failed"
    assert verify_enforce_rotation_capacity_maximum(
        rotations,
        melted_solved_schedule,
    ), "verify_enforce_rotation_capacity_maximum failed"
    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints failed"

    block_schedule = convert_melted_to_block_schedule(melted_solved_schedule)

    print(block_schedule)
