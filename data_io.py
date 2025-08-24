import sqlite3

import pandas as pd
from icecream import ic


def read_bulk_data_sqlite3(
    db_location: str,
    tables_to_read: dict[str, str] | None = None,
    date_fields: dict[str, str] | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Read data from sqlite3 database, extracting tables as requested.

    Converts to datetime where requested and by default to standard data set.

    Returns:
        dict[str, pd.DataFrame]: extracted tables from db
    """
    if tables_to_read is None:
        tables_to_read = {
            "residents",
            "rotations",
            "categories",
            "preferences",
            "weeks",
        }
    if date_fields is None:
        date_field = {"weeks": "monday_date"}

    tables = dict()
    with sqlite3.connect(db_location) as con:
        for table_name in tables_to_read:
            extracted_df = pd.read_sql_query(f"SELECT * FROM {table_name}", con)
            if table_name == "weeks":
                extracted_df["monday_date"] = pd.to_datetime(
                    extracted_df["monday_date"]
                )
            tables.update({table_name: extracted_df})
    return tables


if __name__ == "__main__":
    test_read_tables = read_data_sqlite3("residency_mastermind.db")
    ic(test_read_tables)


def generate_pd_wrapped_boolvar(
    residents: pd.DataFrame, rotations: pd.DataFrame, weeks: pd.DataFrame
) -> pd.DataFrame:
    """

    Args:
        residents: pd.DataFrame of residents
        rotations: pd.DataFrame of rotations
        weeks: pd.DataFrame of weeks

    Returns:
        pd.DataFrame `scheduled`:  wrapped around 3D array of residents, rotations, weeks
        for ease of complex indexing by string variables.
    """

    # Create the 3D boolean variable array
    scheduled_vars = cp.boolvar(
        shape=(len(residents), len(rotations), len(weeks)), name="is_scheduled"
    )

    # Create the MultiIndex DataFrame
    scheduled = pd.DataFrame(
        scheduled_vars.flatten(),
        index=pd.MultiIndex.from_product(
            [residents.full_name, rotations.rotation, weeks.monday_date],
            names=["resident", "rotation", "week"],
        ),
        columns=["is_scheduled_cp_var"],
    )

    return scheduled


if __name__ == "__main__":
    pass
