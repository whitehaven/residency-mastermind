from config import read_config_file
from data_io import read_bulk_data_sqlite3
from main import main
from test_constraints import (
    verify_one_rotation_per_resident_per_week,
    verify_enforce_rotation_capacity_minimum,
)

config = read_config_file()

testing_db_path = config["testing_db_path"]


# TODO make total solution tester
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
