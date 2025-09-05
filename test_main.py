import polars as pl

from config import read_config_file
from display import extract_solved_schedule, convert_melted_to_block_schedule
from main import solve_schedule
from test_constraints import (
    verify_enforce_rotation_capacity_maximum,
    verify_one_rotation_per_resident_per_week,
    verify_enforce_rotation_capacity_minimum,
)

config = read_config_file()
test_residents_path = config["testing_files"]["residents"]["real_size_seniors"]
test_rotations_path = config["testing_files"]["rotations"]["real_size"]
test_weeks_path = config["testing_files"]["weeks"]["full_year"]


def test_main() -> None:
    solved_schedule = main(read_db=testing_db_path)

    input_tables = read_bulk_data_sqlite3(
        db_location=testing_db_path, tables_to_read=("rotations",)
    )
    rotations = input_tables["rotations"]

    assert verify_one_rotation_per_resident_per_week(
        solved_schedule,
    ), "verify_one_rotation_per_resident_per_week failed"
    
    assert verify_enforce_rotation_capacity_minimum(
        rotations,
        solved_schedule,
    ), "verify_enforce_rotation_capacity_minimum failed"
    assert verify_enforce_rotation_capacity_maximum(
        rotations,
        solved_schedule,
    ), "verify_enforce_rotation_capacity_maximum failed"
