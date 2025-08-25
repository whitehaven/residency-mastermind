import polars as pl

from main import main


# TODO make total solution tester
def test_main() -> None:
    """
    Validate that the solution meets all constraints and provide summary stats.

    Args:
        solved_schedule: DataFrame with solved values

    Returns:
        Dictionary with validation results and stats
    """
    solved_schedule = main(read_db="seniors_only.db")

    scheduled_only = solved_schedule.filter(pl.col("is_scheduled_result") == True)
