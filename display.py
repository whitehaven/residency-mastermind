import polars as pl


def extract_solved_schedule(scheduled: pl.DataFrame) -> pl.DataFrame:
    """
    Process decision variable through the attached solver and returns the

    Args:
        scheduled: pl.DataFrame with decision variables

    Returns: scheduled dataframe with a new return column 'is_scheduled_result'

    """
    # MAYBE could make sense to change to return pl.Series of just is_scheduled_result

    solved_values = []
    for decision_variable in scheduled["is_scheduled_cp_var"]:
        solved_values.append(decision_variable.value())
    scheduled_result = scheduled.with_columns(
        pl.Series("is_scheduled_result", solved_values).cast(pl.Boolean)
    )
    return scheduled_result.sort("week")


def convert_to_block_schedule(solved_schedule: pl.DataFrame) -> pl.DataFrame:
    """
    Restructure output into a block schedule with residents as rows and dates as columns with assigned rotation at each intersection.

    Args:
        solved_schedule: df with solved schedule

    Returns:
        block_schedule: pivoted df
    """
    renderable_df = solved_schedule.select(pl.all().exclude("is_scheduled_cp_var"))
    filtered_long_format = renderable_df.filter(pl.col("is_scheduled_result"))
    block_schedule = filtered_long_format.pivot(
        "week", index="resident", values="rotation"
    )
    return block_schedule
