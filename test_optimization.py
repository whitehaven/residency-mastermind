import polars as pl

import config
from optimization import generate_blank_preferences_df

real_size_residents = pl.read_csv(
    config.TESTING_FILES["residents"]["real_size_seniors"]
)
real_size_rotations = pl.read_csv(config.TESTING_FILES["rotations"]["real_size"])
one_academic_year_weeks = pl.read_csv(
    config.TESTING_FILES["weeks"]["full_academic_year_2025_2026"], try_parse_dates=True
)


def test_generate_blank_preferences_df():
    res_list = real_size_residents[config.RESIDENTS_PRIMARY_LABEL].to_list()
    rot_list = real_size_rotations[config.ROTATIONS_PRIMARY_LABEL].to_list()
    week_list = one_academic_year_weeks[config.WEEKS_PRIMARY_LABEL].to_list()

    preferences = generate_blank_preferences_df(res_list, rot_list, week_list)
    assert preferences.shape == (
        len(res_list) * len(rot_list) * len(week_list),
        4,
    ), "generated df is wrong dimension"


def test_minimal_preference_validity():
    raise NotImplementedError
