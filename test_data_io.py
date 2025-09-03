import polars as pl

from config import read_config_file
from data_io import (
    read_bulk_data_sqlite3,
    generate_pl_wrapped_boolvar,
)

config = read_config_file()

tester_residents = pl.read_csv(config["testing_files"]["residents"]["tiny"])
tester_rotations = pl.read_csv(config["testing_files"]["rotations"]["tiny"])
tester_weeks = pl.read_csv(
    config["testing_files"]["weeks"]["tiny"], try_parse_dates=True
)


def test_read_bulk_data_sqlite3():
    tables_in_use = 6
    test_read_tables = read_bulk_data_sqlite3("residency_mastermind.db")

    assert len(test_read_tables) == tables_in_use
    assert isinstance(test_read_tables["residents"], pl.DataFrame)

    dtype_of_weeks_monday_date = (
        test_read_tables["weeks"].select("monday_date").dtypes[0]
    )

    assert isinstance(dtype_of_weeks_monday_date, pl.Date)


def test_generate_pl_wrapped_boolvar():
    fake_scheduled = generate_pl_wrapped_boolvar(
        tester_residents, tester_rotations, tester_weeks
    )
    assert isinstance(fake_scheduled, pl.DataFrame)
    assert len(fake_scheduled) == 54
