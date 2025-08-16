import pandas as pd
import pytest

from data_io import read_data_csv, read_data_sqlite3
from date_handling import generate_weekly_mondays_with_index_df, convert_date_to_academic_yr_and_wk
from interface import generate_resident_preference_dataframe, generate_completed_rotation


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


def test_mondays_generator():
    mondays = generate_weekly_mondays_with_index_df(
        "2025-01-01", "2025-12-31"
    )
    assert isinstance(mondays, pd.DataFrame)
    assert mondays.iloc[0].values == pd.to_datetime("2025-01-06")
    assert len(mondays) == 52


def test_sqlite3_db_import():
    test_read_tables = read_data_sqlite3("residency_mastermind.db")
    assert len(test_read_tables) == 5


def test_generate_completed_rotation():
    single_test = generate_completed_rotation("John Doe, DO", "HS Orange Senior", 4)
    second_test = generate_completed_rotation("John Doe, DO", "STHC Ambulatory Senior", 2)
    test_generated_completed_rotations = pd.concat([single_test, second_test], ignore_index=True)


def test_convert_date_to_academic_yr_and_wk():
    assert convert_date_to_academic_yr_and_wk("2025-06-23") == ("2025-2026", 1)
    assert convert_date_to_academic_yr_and_wk("2025-07-07") == ("2025-2026", 3)
    assert convert_date_to_academic_yr_and_wk("2026-06-22") == ("2026-2027", 1)
    with pytest.raises(AssertionError):
        assert convert_date_to_academic_yr_and_wk("2025-06-01")  # reject out of range too far in past
        assert convert_date_to_academic_yr_and_wk("2027-06-22")  # reject out of range too far in future
        assert convert_date_to_academic_yr_and_wk("John Doe, MD")  # reject wrong column
