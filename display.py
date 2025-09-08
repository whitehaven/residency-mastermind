import box
import polars as pl

config = box.box_from_file("config.yaml")

test_residents_path = config.testing_files.residents.real_size_seniors
test_rotations_path = config.testing_files.rotations.real_size
test_weeks_path = config.testing_files.weeks.full_academic_year_2025_2026
cpmpy_variable_column = config.cpmpy_variable_column
cpmpy_result_column = config.cpmpy_result_column


def extract_solved_schedule(scheduled: pl.DataFrame) -> pl.DataFrame:
    """
    Process decision variable through the attached solver and returns the

    Args:
        scheduled: pl.DataFrame with decision variables

    Returns: scheduled dataframe with a new return column 'is_scheduled_result'

    """
    # MAYBE could make sense to change to return pl.Series of just is_scheduled_result

    solved_values = []

    for decision_variable in scheduled[cpmpy_variable_column]:
        solved_values.append(decision_variable.value())

    scheduled_result = scheduled.with_columns(
        pl.Series(cpmpy_result_column, solved_values).cast(pl.Boolean)
    )
    return scheduled_result.sort("week")


def convert_melted_to_block_schedule(solved_schedule: pl.DataFrame) -> pl.DataFrame:
    """
    Restructure output into a block schedule with residents as rows and dates as columns with assigned rotation at each intersection.

    Args:
        solved_schedule: df with solved schedule

    Returns:
        block_schedule: pivoted df
    """
    # TODO should catch unrenderable/not 1:1 before Polars fails ugly on it
    renderable_df = solved_schedule.select(pl.all().exclude(cpmpy_variable_column))
    filtered_long_format = renderable_df.filter(pl.col(cpmpy_result_column))
    block_schedule = filtered_long_format.pivot(
        "week", index="resident", values="rotation"
    )
    return block_schedule
