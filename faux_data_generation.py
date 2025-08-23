import numpy as np
import pandas as pd
from faker import Faker


def generate_fake_residents(residents_structure: dict) -> pd.DataFrame:
    fake = Faker()

    faked_residents = {}

    roles_mapping = {
        "TY1": "TY",
        "PMR1": "PMR",
        "R1": "IM-Intern",
        "R2": "IM-Senior",
        "R3": "IM-Senior",
    }

    for year, count in residents_structure.items():
        for resident_index in range(count):
            faked_residents.update(
                {
                    f"{year}_{resident_index}": {
                        "full_name": f"{fake.first_name()} {fake.last_name()} {fake.random_element(["MD", "DO"])}",
                        "year": year,
                        "role": roles_mapping[year],
                    }
                }
            )

    return pd.DataFrame.from_dict(faked_residents, orient="index")


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


def generate_completed_rotation(resident: str, rotation: str, weeks: int) -> pd.DataFrame:
    return pd.DataFrame({"resident": [resident], "rotation": [rotation], "weeks": [weeks]})


if __name__ == "__main__":
    pass


def grab_tester_residents():
    return pd.DataFrame(
        {
            "full_name": ["Fake Person, MD", "Also Fake Person, MD"],
            "year": ["R3", "R3"],
            "role": ["IM-Senior", "IM-Senior"],
            "track": ["Hospitalist", "Primary Care Track"],
        }
    )


def grab_tester_rotations():
    return pd.DataFrame(
        {
            "rotation": ["Green HS Senior", "Orange HS Senior", "SHMC Consults"],
            "category": ["HS Rounding Senior", "HS Rounding Senior", "Hospitalist"],
            "required_role": ["Senior", "Senior", "Senior"],
            "minimum_weeks": [0, 0, 0],
            "maximum_weeks": [8, 8, 4],
            "minimum_residents_assigned": [1, 1, 0],
            "maximum_residents_assigned": [1, 1, 1],
            "minimum_contiguous_weeks": [2, 2, 1],
            "max_contiguous_weeks": [np.nan, np.nan, np.nan],
        }
    )


def grab_tester_weeks():
    return pd.DataFrame(
        {
            "monday_date": [
                "2025-06-23",
                "2025-06-30",
                "2025-07-07",
                "2025-07-14",
                "2025-07-21",
                "2025-07-28",
                "2025-08-04",
                "2025-08-11",
                "2025-08-18",
            ],
            "week": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "starting_academic_year": [
                2025,
                2025,
                2025,
                2025,
                2025,
                2025,
                2025,
                2025,
                2025,
            ],
            "ending_academic_year": [
                2026,
                2026,
                2026,
                2026,
                2026,
                2026,
                2026,
                2026,
                2026,
            ],
        }
    )
