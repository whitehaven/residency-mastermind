import itertools as it

import polars as pl

import config

real_size_residents = pl.read_csv(config.TESTING_FILES["residents"]["real_size_seniors"])
real_size_rotations = pl.read_csv(config.TESTING_FILES["rotations"]["real_size"])
one_academic_year_weeks = pl.read_csv(
    config.TESTING_FILES["weeks"]["full_academic_year_2025_2026"], try_parse_dates=True
)

def generate_blank_preferences_df(
    resident_list: list, rotations_list: list, weeks_list: list
) -> pl.DataFrame:
    blank_preferences = pl.DataFrame(
        list(
            it.product(
                resident_list,
                rotations_list,
                weeks_list,
            )
        ),
        orient="row",
    )
    blank_preferences = blank_preferences.with_columns(preference=pl.lit(0))
    return blank_preferences