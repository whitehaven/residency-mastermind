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


def read_data_sqlite3(db_location: str, tables_and_indexes_to_read: dict[str, str] | None = None) -> dict[
    str, pd.DataFrame]:
    """
    Read data from sqlite3 database, extracting tables as requested.

    Returns:
        dict[str, pd.DataFrame]: extracted tables from db
    """
    if tables_and_indexes_to_read is None:
        tables_and_indexes_to_read = {"residents": "full_name", "rotations": "rotation", "categories": "category_name",
                                      "preferences": "full_name", "weeks": "week"}

    tables = dict()
    with sqlite3.connect(db_location) as con:
        for table_name, index in tables_and_indexes_to_read.items():
            extracted_df = pd.read_sql_query(f"SELECT * FROM {table_name}", con, index_col=index)
            tables.update({table_name: extracted_df})
    return tables


if __name__ == "__main__":
    test_read_tables = read_data_sqlite3("residency_mastermind.db")
    ic(test_read_tables)
