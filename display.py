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


# TODO rotate result dataframe ultimately to emit an Excel table to mimic the original schedule.
