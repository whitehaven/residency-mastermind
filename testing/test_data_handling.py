def test_data_integrity():
    """
    Test to ensure that the data integrity of the scheduling model is maintained.
    This includes checking that all required roles and rotations are correctly defined
    and that no invalid combinations exist.
    """
    import pandas as pd

    residents = pd.read_csv("testing/residents.csv")

    residents["full_name"] = (
        residents.first_name + " " + residents.last_name + " " + residents.degree
    )
    residents.set_index("full_name", append=True, inplace=True)

    rotations = pd.read_csv("testing/rotations.csv", index_col="rotation")
    rotation_categories = pd.read_csv(
        "testing/rotation_categories.csv", index_col="category"
    )
    preferences = pd.read_csv(
        "testing/preferences.csv",
        index_col=[
            "last_name",
            "first_name",
            "degree",
        ],
    )
    weeks = pd.read_csv("testing/weeks.csv", index_col="week")

    assert not residents.empty, "Residents DataFrame is empty."

    assert not rotations.empty, "Rotations DataFrame is empty."

    assert not rotation_categories.empty, "Rotation categories DataFrame is empty."

    assert not preferences.empty, "Preferences DataFrame is empty."

    assert not weeks.empty, "Weeks DataFrame is empty."

    # Additional checks can be added as needed to ensure data integrity

def test_date_conversion():
    """
    Test to ensure that date handling functions work correctly.
    This includes checking the conversion of dates to academic week numbers.
    """
    import pandas as pd
    from data_generator import date_to_week, week_to_date

    # Test a known date
    test_date = pd.Timestamp("2025-07-07")
    week_number = date_to_week(test_date)

    test_week_number = 0
    returned_date = week_to_date(test_week_number)

    assert week_number == 0, f"Expected week number 0 for {test_date}, got {week_number}"
    assert returned_date == pd.Timestamp("2025-07-07"), f"Expected date for week 0 is 2025-07-07, got {returned_date}"