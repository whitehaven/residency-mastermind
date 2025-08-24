import pandas as pd

from data_io import read_data_sqlite3, generate_pd_wrapped_boolvar
from testing_helpers import (
    grab_tester_residents,
    grab_tester_rotations,
    grab_tester_weeks,
)


def test_sqlite3_db_import():
    test_read_tables = read_data_sqlite3("residency_mastermind.db")
    assert len(test_read_tables) == 5


def test_generate_pd_wrapped_boolvar():
    fake_scheduled = generate_pd_wrapped_boolvar(
        grab_tester_residents(), grab_tester_rotations(), grab_tester_weeks()
    )
    assert isinstance(fake_scheduled, pd.DataFrame)
    assert len(fake_scheduled) == 54
