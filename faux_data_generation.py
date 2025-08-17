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
