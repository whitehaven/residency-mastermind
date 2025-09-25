import box
import polars as pl

from config import config
from display import extract_solved_schedule, convert_melted_to_block_schedule
from main import solve_schedule
from test_constraints import (
    verify_enforce_rotation_capacity_maximum,
    verify_one_rotation_per_resident_per_week,
    verify_enforce_rotation_capacity_minimum,
    verify_minimum_contiguity,
    verify_enforce_requirement_constraints,
)

test_residents_path = config.testing_files.residents.real_size_seniors
test_rotations_path = config.testing_files.rotations.real_size
test_weeks_path = config.testing_files.weeks.full_academic_year_2025_2026


def test_solve_schedule():
    residents = pl.read_csv(test_residents_path)
    rotations = pl.read_csv(test_rotations_path)
    weeks = pl.read_csv(test_weeks_path, try_parse_dates=True)
    current_requirements = box.box_from_file(config.default_requirements_path)

    non_extended_residents = residents.filter((pl.col("year").is_in({"R2", "R3"})))

    scheduled = solve_schedule(non_extended_residents, rotations, weeks)

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
    assert verify_minimum_contiguity(
        rotations, melted_solved_schedule
    ), "verify_minimum_contiguity failed"
    assert verify_enforce_requirement_constraints(
        current_requirements,
        non_extended_residents,
        rotations,
        weeks,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints failed"

    block_schedule = convert_melted_to_block_schedule(melted_solved_schedule)
