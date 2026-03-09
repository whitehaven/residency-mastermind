import polars as pl
import pytest

import config
from data_io import (
    generate_pl_wrapped_boolvar,
)


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
