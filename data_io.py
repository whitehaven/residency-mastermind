import sqlite3

import pandas as pd
from icecream import ic


def read_data_csv() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Read data from CSV files and prepare DataFrames for residents, rotations,
    rotation categories, preferences, and weeks.
    """
    residents = pd.read_csv("testing/residents.csv")

    residents.set_index("full_name", append=False, inplace=True)

    rotations = pd.read_csv("testing/rotations.csv", index_col="rotation")
    rotation_categories = pd.read_csv(
        "testing/rotation_categories.csv", index_col="category"
    )
    preferences = pd.read_csv(
        "testing/preferences.csv",
        index_col=[
            "full_name",
        ],
    )
    weeks = pd.read_csv("testing/weeks.csv", index_col="week")

    return residents, rotations, rotation_categories, preferences, weeks


def read_data_sqlite3(db_location: str) -> dict[str, pd.DataFrame]:
    tables = dict()
    with sqlite3.connect(db_location) as con:
        for table in ["residents", "rotations", "rotation_categories", "preferences", "weeks"]:
            df = pd.read_sql_query(f"SELECT * FROM {table}", con)
            tables.update({table: df})
    return tables


if __name__ == "__main__":
    test_read_tables = read_data_sqlite3("testing/residency_mastermind_inputs.db")
    ic(test_read_tables)
