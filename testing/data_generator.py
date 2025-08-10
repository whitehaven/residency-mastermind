import numpy as np
import pandas as pd
from faker import Faker
from icecream import ic

first_day_2025_academic_year = pd.Timestamp("2025-07-07")

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
                        "last_name": fake.last_name(),
                        "first_name": fake.first_name(),
                        "degree": fake.random_element(
                            elements=(
                                "MD",
                                "DO",
                            )
                        ),
                        "year": year,
                        "role": roles_mapping[year],
                    }
                }
            )

    return pd.DataFrame.from_dict(faked_residents, orient="index")

def get_rotations_needing_preferences(
    residents: pd.DataFrame, rotations: pd.DataFrame, rotation_categories: pd.DataFrame
) -> pd.DataFrame:

    fake = Faker()

    rotations_with_categories = pd.merge(
        left=rotations,
        right=rotation_categories,
        left_on="category",
        right_index=True,
        how="inner",
        suffixes=("_rotation", "_category"),
    )

    elective_rotations = rotations_with_categories.loc[
        rotations_with_categories.elective == "elective"
    ]

    # it.product(elective_rotations.index, residents.index)

    return elective_rotations


def generate_week_mapping() -> pd.DataFrame:
    weekly_2025_index = pd.date_range(start=first_day_2025_academic_year, periods=52, freq="W-MON")
    week_to_date = pd.DataFrame(
        {"date": weekly_2025_index, "week": range(len(weekly_2025_index))}
    ).set_index("week")
    return week_to_date

def week_to_date(week: int) -> pd.Timestamp:
    """
    Convert academic year week number to date
    """
    weeks = pd.read_csv("testing/weeks.csv", index_col="week", parse_dates=["date"])
    return weeks.loc[week, "date"] # type: ignore | works as tested

def date_to_week(date: pd.Timestamp) -> int:
    """
    Convert date to academic year week number
    """
    weeks = pd.read_csv("testing/weeks.csv", index_col="week", parse_dates=["date"])
    return weeks[weeks["date"] == date].index[0]


if __name__ == "__main__":
    fake = Faker()

    generate_new_residents = False
    generate_new_preferences = False
    generate_weeks = False

    if generate_fake_residents:

        current_residency_structure = {
            "TY1": 8,
            "PMR1": 8,
            "R1": 10,
            "R2": 10,
            "R3": 10,
        }

        fake_residents = generate_fake_residents(current_residency_structure)
        fake_residents.to_csv("testing/residents.csv", index=False)

    # this test presumes real structure of rotations, rotation categories, and prerequisites are in place - can't generate these randomly
    residents = pd.read_csv("testing/residents.csv", index_col="last_name")
    rotations = pd.read_csv("testing/rotations.csv", index_col="rotation")
    rotation_categories = pd.read_csv(
        "testing/rotation_categories.csv", index_col="category"
    )

    if generate_new_preferences:

        fake_preferences = generate_fake_preferences(
            residents=residents,
            rotations=rotations,
            rotation_categories=rotation_categories,
        )
        fake_preferences.to_csv("testing/preferences.csv", index=False)

    preferences = pd.read_csv(
        "testing/preferences.csv",
        index_col=[
            "last_name",
            "first_name",
            "degree",
        ],
    )

    if generate_weeks:
        generate_week_mapping().to_csv("testing/weeks.csv", index=True)

    weeks = pd.read_csv("testing/weeks.csv", index_col="week")

    ic(residents.head())
    ic(rotations.head())
    ic(rotation_categories.head())
    ic(preferences.head())
    ic(weeks.head())
    ic("All test data is in place.")
