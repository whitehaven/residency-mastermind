import pandas as pd
from icecream import ic

from data_handler import read_data


def generate_resident_preference_dataframe(
    resident: str,
    rotation: str,
    week: int | tuple[int, int] | None,
    weeks: pd.DataFrame,
    preference_value: int,
) -> pd.DataFrame:
    """
    Generate a DataFrame with a single resident's preference for a specific rotation and week or week range.

    Args:
        resident (str): Full name of the resident.
        rotation (str): Name of the rotation.
        week (int | tuple[int, int] | None): Week number or a tuple of start and end week numbers. If None, applies to all weeks in the rotation.
        weeks (pd.DataFrame): DataFrame containing week information.
        preference_value (int): Preference value to set.

    Returns:
        pd.DataFrame: DataFrame containing the resident's preference.
    """

    if week is None:
        generated_preferences = pd.DataFrame(
            {
                "full_name": [resident] * len(weeks),
                "rotation": [rotation] * len(weeks),
                "week": range(len(weeks)),
                "preference": [preference_value] * len(weeks),
            }
        )
    elif isinstance(week, tuple) and len(week) == 2:
        start_week, end_week = week
        generated_preferences = pd.DataFrame(
            {
                "full_name": [resident] * (end_week - start_week + 1),
                "rotation": [rotation] * (end_week - start_week + 1),
                "week": range(start_week, end_week + 1),
                "preference": [preference_value] * (end_week - start_week + 1),
            }
        )
    elif isinstance(week, int):
        assert week in weeks.index, f"Week {week} is not in the weeks DataFrame."
        generated_preferences = pd.DataFrame(
            {
                "full_name": [resident],
                "rotation": [rotation],
                "week": week,
                "preference": [preference_value],
            }
        )
    else:
        raise ValueError("Week must be an int, tuple of ints, or None.")

    return generated_preferences

    
if __name__ == "__main__":
    
    residents, rotations, rotation_categories, preferences, weeks = read_data()

    preferences = generate_resident_preference_dataframe(
        resident="John Doe, DO",
        rotation="Rotation1",
        week=(0, 3),
        weeks=pd.read_csv("testing/weeks.csv", index_col="week"),
        preference_value=3,
    )
    ic(preferences)

    test_preferences_single_week = generate_resident_preference_dataframe(
        resident="John Doe, DO",
        rotation="Rotation1",
        week=0,
        weeks=weeks,
        preference_value=5,
    )
    ic(test_preferences_single_week)

    test_preferences_all_weeks = generate_resident_preference_dataframe(
    resident="John Doe, DO",
    rotation="Rotation1",
    week=None,
    weeks=weeks,
    preference_value=2,
)
    ic(test_preferences_all_weeks)