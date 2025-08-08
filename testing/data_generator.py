import pandas as pd
from faker import Faker
from icecream import ic
import numpy as np


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


def generate_fake_preferences(
    residents: pd.DataFrame, rotations: pd.DataFrame, rotation_categories: pd.DataFrame
) -> pd.DataFrame:

    fake = Faker()

    rotations_needing_preferences = get_rotations_needing_preferences(
        residents=residents,
        rotations=rotations,
        rotation_categories=rotation_categories,
    )

    residents["mapped_role"] = residents.role.replace(
        {"IM-Senior": "Senior", "IM-Intern": "Any", "PMR": "Any", "TY": "Any"}
    )
    residents = residents.reset_index()
    rotations_needing_preferences = get_rotations_needing_preferences(
        residents, rotations, rotation_categories
    )

    resident_to_elective_mapping = pd.merge(
        rotations_needing_preferences,
        residents,
        left_on="required_role",
        right_on="mapped_role",
        how="inner",
    ).loc[
        :,
        [
            "category",
            "last_name",
            "first_name",
            "degree",
            "year",
            "role",
            "mapped_role",
        ],
    ]
    resident_to_elective_mapping["preference"] = np.random.randint(
        0, 10 + 1, size=len(resident_to_elective_mapping)
    )

    return resident_to_elective_mapping


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


if __name__ == "__main__":
    fake = Faker()

    generate_new_residents = False
    generate_new_preferences = False

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


    ic(residents.head())
    ic(rotations.head())
    ic(rotation_categories.head())
    ic(preferences.head())
    ic("All test data is in place.")