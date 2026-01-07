import itertools
import sqlite3

import cpmpy as cp
import polars as pl
import yaml


def read_bulk_data_sqlite3(
    db_location: str,
    tables_to_read: tuple[str, ...] | None = None,
    date_fields: dict[str, str] | None = None,
) -> dict[str, pl.DataFrame]:
    """
    Read data from sqlite3 database, extracting tables as requested. Defaults to pulling all tables normally used in schedule building.

    Converts to datetime where requested and by default to standard data set.

    Returns:
        dict[str, pd.DataFrame]: extracted tables from db
    """
    if tables_to_read is None:
        tables_to_read = (
            "residents",
            "rotations",
            "weeks",
        )
    if date_fields is None:
        date_fields = {"weeks": "monday_date"}

    tables = dict()
    with sqlite3.connect(db_location) as con:
        for table_name in tables_to_read:
            extracted_df = pl.read_database(f"SELECT * FROM {table_name}", con)
            if table_name in date_fields:
                extracted_df = extracted_df.with_columns(pl.coalesce(
                    pl.col(date_fields[table_name]).str.strptime(pl.Date,"%F",strict=False),
                    pl.col(date_fields[table_name]).str.strptime(pl.Date,"%D", strict=False),
                ))
            tables.update({table_name: extracted_df})
    return tables


def generate_pl_wrapped_boolvar(
    residents: pl.DataFrame, rotations: pl.DataFrame, weeks: pl.DataFrame
) -> pl.DataFrame:
    """
    Generate a Polars DataFrame wrapper around 3D CP-SAT boolean variables.

    Args:
        residents: pl.DataFrame of residents
        rotations: pl.DataFrame of rotations
        weeks: pl.DataFrame of weeks

    Returns:
        pl.DataFrame `scheduled`: wrapped around 3D array of residents, rotations, weeks
        for ease of complex indexing by string variables.
    """

    residents_list = residents["full_name"].to_list()
    rotations_list = rotations["rotation"].to_list()
    weeks_list = weeks["monday_date"].to_list()
    combinations = list(itertools.product(residents_list, rotations_list, weeks_list))

    variable_labels = [f"boolvar@({combo[0]}, {combo[1]}, {combo[2]})" for combo in combinations]

    scheduled_vars: list[str] = cp.boolvar(
        shape=(len(residents) * len(rotations) * len(weeks)), name=variable_labels  # type: ignore
    )

    scheduled = pl.DataFrame(
        {
            "resident": [combo[0] for combo in combinations],
            "rotation": [combo[1] for combo in combinations],
            "week": [combo[2] for combo in combinations],
            "is_scheduled_cp_var": scheduled_vars.flatten(),  # type: ignore
        }
    )

    scheduled = scheduled.with_columns(
        pl.col("week").str.to_datetime()
        if scheduled["week"].dtype == pl.Utf8
        else pl.col("week")
    )

    years_col = scheduled.join(
        residents, left_on="resident", right_on="full_name"
    ).select("year")
    scheduled_with_resident_year = pl.concat([scheduled, years_col], how="horizontal")
    scheduled_with_resident_year_and_ordered = scheduled_with_resident_year.select(
        "resident", "year", "rotation", "week", "is_scheduled_cp_var"
    )

    return scheduled_with_resident_year_and_ordered


def dump_polars_df_to_yaml(df: pl.DataFrame) -> str:
    return yaml.dump(df.to_dicts())
