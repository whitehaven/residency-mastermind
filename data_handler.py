def read_data():
    """
    Read data from CSV files and prepare DataFrames for residents, rotations,
    rotation categories, preferences, and weeks.
    """
    import pandas as pd

    residents = pd.read_csv("testing/residents.csv")

    residents["full_name"] = (
        residents.first_name + " " + residents.last_name + " " + residents.degree
    )
    residents.set_index("full_name", append=False, inplace=True)

    rotations = pd.read_csv("testing/rotations.csv", index_col="rotation")
    rotation_categories = pd.read_csv(
        "testing/rotation_categories.csv", index_col="category"
    )
    preferences = pd.read_csv(
        "testing/preferences.csv",
        index_col=[
            "last_name",
            "first_name",
            "degree",
        ],
    )
    weeks = pd.read_csv("testing/weeks.csv", index_col="week")

    return residents, rotations, rotation_categories, preferences, weeks