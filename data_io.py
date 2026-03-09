import itertools

import cpmpy as cp
import polars as pl
import yaml


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

    variable_labels = [
        f"boolvar@({combo[0]}, {combo[1]}, {combo[2]})" for combo in combinations
    ]

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
