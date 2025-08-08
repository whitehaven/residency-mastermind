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



if __name__ == "__main__":
    fake = Faker()

    current_residency_structure = {"TY1": 8, "PMR1": 8, "R1": 10, "R2": 10, "R3": 10}

    fake_residents = generate_fake_residents(current_residency_structure)
    fake_residents.to_csv("testing/residents.csv", index=False)

    # this test presumes real structure of rotations, rotation categories, and prerequisites are in place - can't generate these randomly
    residents = pd.read_csv("testing/residents.csv", index_col="last_name")
    rotations = pd.read_csv("testing/rotations.csv", index_col="rotation_name")
    rotation_categories = pd.read_csv(
        "testing/rotation_categories.csv", index_col="category"
    )

    ic(residents.head())
    ic(rotations.head())
    ic(rotation_categories.head())

    # fake_preferences = generate_fake_preferences(residents=fake_residents, rotations=rotations, rotation_categories=rotation_categories)
    # fake_preferences.to_csv("testing/preferences.csv", index=False)
