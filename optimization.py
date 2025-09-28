import itertools as it

import polars as pl

from config import config

cpmpy_variable_column = config.cpmpy_variable_column
cpmpy_result_column = config.cpmpy_result_column

real_size_residents = pl.read_csv(config.testing_files.residents.real_size_seniors)
real_size_rotations = pl.read_csv(config.testing_files.rotations.real_size)
one_academic_year_weeks = pl.read_csv(
    config.testing_files.weeks.full_academic_year_2025_2026, try_parse_dates=True
)

default_solver = config.default_cpmpy_solver


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


if __name__ == "__main__":
    res_list = real_size_residents[config.residents_primary_label].to_list()
    rot_list = real_size_rotations[config.rotations_primary_label].to_list()
    week_list = one_academic_year_weeks[config.weeks_primary_label].to_list()
    generate_blank_preferences_df(res_list, rot_list, week_list)
