from interface import set_resident_preference


def test_set_resident_preference():
    import pandas as pd

    # Create a sample preferences DataFrame
    preferences = pd.DataFrame(
        {
            "full_name": ["John Doe, DO", "Jane Smith, MD"],
            "rotation": ["Rotation1", "Rotation2"],
            "week": [1, 2],
            "preference": [0, 0],
        }
    )

    # Set preference for a specific resident and rotation
    set_resident_preference(preferences, "John Doe, DO", "Rotation1", 1, 5)

    # Check if the preference was set correctly
    assert (
        preferences.loc[
            (preferences["full_name"] == "John Doe, DO")
            & (preferences["rotation"] == "Rotation1")
            & (preferences["week"] == 1),
            "preference",
        ].values[0]
        == 5
    )

    # Set preference for all weeks in a rotation
    set_resident_preference(preferences, "Jane Smith, MD", "Rotation2", None, 3)

    # Check if the preference was set for all weeks
    assert all(
        preferences.loc[
            (preferences["full_name"] == "Jane Smith, MD")
            & (preferences["rotation"] == "Rotation2"),
            "preference",
        ]
        == 3
    )
