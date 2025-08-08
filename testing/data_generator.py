import pandas as pd
from faker import Faker
from icecream import ic
import numpy as np


def generate_fake_residents_csv(
    filename, residents_structure={"TY1": 8, "PMR1": 8, "R1": 10, "R2": 10, "R3": 10}
) -> None:
    if residents_structure:
        residents_to_generate = residents_structure

    fake = Faker()

    faked_residents = {}

    roles_mapping = {
        "TY1": "TY",
        "PMR1": "PMR",
        "R1": "IM-Intern",
        "R2": "IM-Senior",
        "R3": "IM-Senior",
    }

    for year, count in residents_to_generate.items():
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

    df = pd.DataFrame.from_dict(faked_residents, orient="index")
    df.to_csv(filename, index=False)
    print(f"Generated {filename} with fake residents data.")


if __name__ == "__main__":
    fake = Faker()
    generate_fake_residents_csv("./testing/residents.csv")
