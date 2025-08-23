import pandas as pd

from data_io import read_data_csv, read_data_sqlite3, generate_pd_wrapped_boolvar
from faux_data_generation import (
    generate_resident_preference_dataframe,
    generate_completed_rotation,
    grab_tester_residents,
    grab_tester_rotations,
    grab_tester_weeks,
)


def test_set_resident_preference():
    residents, rotations, rotation_categories, preferences, weeks = read_data_csv()

    test_preferences_single_week = generate_resident_preference_dataframe(
        resident="John Doe, DO",
        rotation="Rotation1",
        week=0,
        weeks=weeks,
        preference_value=5,
    )

    assert isinstance(
        test_preferences_single_week, pd.DataFrame
    ), "Test preferences DataFrame is not a DataFrame."
    assert (
            len(test_preferences_single_week) == 1
    ), "Test preferences DataFrame should have one row."
    assert (
            test_preferences_single_week["full_name"].iloc[0] == "John Doe, DO"
    ), "Resident name not set right."

    test_preferences_multiple_weeks = generate_resident_preference_dataframe(
        resident="John Doe, DO",
        rotation="Rotation1",
        week=(0, 3),
        weeks=weeks,
        preference_value=3,
    )

    assert isinstance(
        test_preferences_multiple_weeks, pd.DataFrame
    ), "Test preferences DataFrame is not a DataFrame."
    assert (
            len(test_preferences_multiple_weeks) == 4
    ), "Test preferences DataFrame should have 4 rows."

    test_preferences_all_weeks = generate_resident_preference_dataframe(
        resident="John Doe, DO",
        rotation="Rotation1",
        week=None,
        weeks=weeks,
        preference_value=2,
    )

    assert isinstance(
        test_preferences_all_weeks, pd.DataFrame
    ), "Test preferences DataFrame is not a DataFrame."
    assert len(test_preferences_all_weeks) == len(
        weeks
    ), "Test preferences DataFrame should have the same number of rows as master weeks DataFrame."


def test_sqlite3_db_import():
    test_read_tables = read_data_sqlite3("residency_mastermind.db")
    assert len(test_read_tables) == 5


def test_generate_completed_rotation():
    single_test = generate_completed_rotation("John Doe, DO", "HS Orange Senior", 4)
    second_test = generate_completed_rotation(
        "John Doe, DO", "STHC Ambulatory Senior", 2
    )
    test_generated_completed_rotations = pd.concat(
        [single_test, second_test], ignore_index=True
    )


def test_generate_pd_wrapped_boolvar():
    fake_scheduled = generate_pd_wrapped_boolvar(
        grab_tester_residents(), grab_tester_rotations(), grab_tester_weeks()
    )
    assert isinstance(fake_scheduled, pd.DataFrame)
    assert len(fake_scheduled) == 54
