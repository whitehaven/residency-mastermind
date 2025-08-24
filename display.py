import polars as pl


def print_full_dataframe(df):
    """
    Prints a DataFrame in full, overriding truncation, then resets the option.
    Source: https://stackoverflow.com/questions/2058552/how-to-print-a-pandas-data
    """
    import pandas as pd

    pd.set_option("display.max_rows", len(df))
    print(df)
    pd.reset_option("display.max_rows")
    return None


def extract_solved_schedule(scheduled):
    solved_values = []
    for decision_variable in scheduled["is_scheduled_cp_var"]:
        solved_values.append(decision_variable.value())
    scheduled_result = scheduled.with_columns(
        pl.Series("is_scheduled_value", solved_values).cast(pl.Boolean)
    )
    return scheduled_result
