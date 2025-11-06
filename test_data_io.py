import polars as pl
import pytest

import config
from data_io import (
    read_bulk_data_sqlite3,
    generate_pl_wrapped_boolvar,
)


@pytest.mark.skip("project not currently using sqlite, return to this later")
def test_read_bulk_data_sqlite3():
    test_read_tables = read_bulk_data_sqlite3(config.TESTING_DB_PATH)
    assert isinstance(test_read_tables["residents"], pl.DataFrame)

    dtype_of_weeks_monday_date = (
        test_read_tables["weeks"].select("monday_date").dtypes[0]
    )
    assert isinstance(
        dtype_of_weeks_monday_date, pl.Date
    ), "weeks monday_date column type != pl.Date"


def test_generate_pl_wrapped_boolvar():
    tester_residents = pl.read_csv(config.TESTING_FILES["residents"]["real_size_seniors"])
    tester_rotations = pl.read_csv(config.TESTING_FILES["rotations"]["real_size"])
    tester_weeks = pl.read_csv(
        config.TESTING_FILES["weeks"]["full_academic_year_2025_2026"], try_parse_dates=True
    )

    fake_scheduled = generate_pl_wrapped_boolvar(
        tester_residents, tester_rotations, tester_weeks
    )
    assert isinstance(fake_scheduled, pl.DataFrame)
