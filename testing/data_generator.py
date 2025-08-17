import pandas as pd
from faker import Faker
from icecream import ic


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

    if generate_fake_residents:
        current_residency_structure = {
            "TY1": 8,
            "PMR1": 8,
            "R1": 10,
            "R2": 10,
            "R3": 10,
        }

        fake_residents = generate_fake_residents(current_residency_structure)
        fake_residents.to_csv("residents.csv", index=False)

    # this test presumes real structure of rotations, rotation categories, and prerequisites are in place - can't generate these randomly
    residents = pd.read_csv("residents.csv", index_col="full_name")
    rotations = pd.read_csv("rotations.csv", index_col="rotation")
    rotation_categories = pd.read_csv(
        "rotation_categories.csv", index_col="category"
    )

    preferences = pd.read_csv(
        "preferences.csv",
        index_col=["full_name"],
    )

    weeks = pd.read_csv("weeks.csv", index_col="week")

    ic(residents.head())
    ic(rotations.head())
    ic(rotation_categories.head())
    ic(preferences.head())
    ic(weeks.head())
    ic("All test data is in place.")
