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
