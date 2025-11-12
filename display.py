import polars as pl

import config

test_residents_path = pl.read_csv(config.TESTING_FILES["residents"]["real_size_seniors"])
test_rotations_path = pl.read_csv(config.TESTING_FILES["rotations"]["real_size"])
test_weeks_path = config.TESTING_FILES["weeks"]["full_academic_year_2025_2026"]

def extract_solved_schedule(scheduled: pl.DataFrame) -> pl.DataFrame:
    """
    Process decision variable through the attached solver and returns the

    Args:
        scheduled: pl.DataFrame with decision variables

    Returns: scheduled dataframe with a new return column 'is_scheduled_result'

    """
    # MAYBE could make sense to change to return pl.Series of just is_scheduled_result

    solved_values = []

    for decision_variable in scheduled[config.CPMPY_VARIABLE_COLUMN]:
        solved_values.append(decision_variable.value())

    scheduled_result = scheduled.with_columns(
        pl.Series(config.CPMPY_RESULT_COLUMN, solved_values).cast(pl.Boolean)
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
    renderable_df = solved_schedule.select(pl.all().exclude(config.CPMPY_VARIABLE_COLUMN))
    filtered_long_format = renderable_df.filter(pl.col(config.CPMPY_RESULT_COLUMN))
    block_schedule = filtered_long_format.pivot(
        "week", index="resident", values="rotation"
    )
    if block_schedule.is_empty():
        raise ValueError(
            f"{block_schedule.is_empty()=}, usually occurs because > 1 True rotation slot per resident:week locus"
        )
    return block_schedule


def reconstruct_melted_from_block_schedule(
    block_schedule: pl.DataFrame,
) -> pl.DataFrame:
    """
    Rebuild melted schedule from block. Keep in mind it only returns True loci because False values don't carry through in convert_melted_to_block_schedule
    Args:
        block_schedule:
    Returns:
        reconstructed_melted_schedule: again, the True-only variable components are all that will reappear.
    """
    unpivoted = block_schedule.unpivot(index=config.BLOCK_SCHEDULE_INDEX)
    unpivoted_with_true_literal = unpivoted.with_columns(
        pl.lit(value=True).alias(config.CPMPY_RESULT_COLUMN)
    )
    return unpivoted_with_true_literal
