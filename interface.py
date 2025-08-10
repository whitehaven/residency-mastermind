import pandas as pd


def set_resident_preference(
    preferences: pd.DataFrame,
    resident: str,
    rotation: str,
    week: int | tuple[int, int] | None,
    preference_value: int,
) -> None:
    """
    Set a resident's preference for a specific rotation and week or week range. Alternatively, set a preference for all weeks in the rotation if week is None.

    Args:
        preferences (pd.DataFrame): DataFrame containing preferences.
        resident (str): Full name of the resident.
        rotation (str): Name of the rotation.
        week (int | tuple[int, int] | None): Week number or a tuple of start and end week numbers. If None, applies to all weeks in the rotation.
        preference_value (int): Preference value to set.
    """
    if week is None:
        # Set preference for all weeks in the rotation
        preferences.loc[
            (preferences["full_name"] == resident)
            & (preferences["rotation"] == rotation),
            "preference",
        ] = preference_value
    elif isinstance(week, tuple):
        # Set preference for a range of weeks
        start_week, end_week = week
        preferences.loc[
            (preferences["full_name"] == resident)
            & (preferences["rotation"] == rotation)
            & (preferences["week"].between(start_week, end_week)),
            "preference",
        ] = preference_value
    else:
        # Set preference for a single week
        preferences.loc[
            (preferences["full_name"] == resident)
            & (preferences["rotation"] == rotation)
            & (preferences["week"] == week),
            "preference",
        ] = preference_value
