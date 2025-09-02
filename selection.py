import polars as pl

from config import read_config_file

config = read_config_file()
cpmpy_variable_column = config["cpmpy_variable_column"]
cpmpy_result_column = config["cpmpy_result_column"]
default_solver = config["default_cpmpy_solver"]


def get_resident_week_vars(
    scheduled: pl.DataFrame, resident_name: str, week_date
) -> list:
    # TODO test if works
    """Get all rotation variables for a specific resident and week."""
    return scheduled.filter(
        (pl.col("resident") == resident_name) & (pl.col("week") == week_date)
    )[cpmpy_variable_column].to_list()


def get_rotation_week_vars(
    scheduled: pl.DataFrame, rotation_name: str, week_date
) -> list:
    # TODO test if works
    """Get all resident variables for a specific rotation and week."""
    return scheduled.filter(
        (pl.col("rotation") == rotation_name) & (pl.col("week") == week_date)
    )[cpmpy_variable_column].to_list()


def get_resident_rotation_vars(
    scheduled: pl.DataFrame, resident_name: str, rotation_name: str
) -> list:
    # TODO test if works
    """Get all week variables for a specific resident and rotation."""
    return scheduled.filter(
        (pl.col("resident") == resident_name) & (pl.col("rotation") == rotation_name)
    )[cpmpy_variable_column].to_list()


def subset_scheduled_by(residents, rotations, weeks, scheduled):
    resident_names = residents["full_name"].to_list()
    rotation_names = rotations["rotation"].to_list()
    week_dates = weeks["monday_date"].to_list()
    subset_scheduled = scheduled.filter(
        (pl.col("resident").is_in(resident_names))
        & (pl.col("rotation").is_in(rotation_names))
        & (pl.col("week").is_in(week_dates))
    )
    return subset_scheduled


def group_scheduled_df_by_for_each(
    subset_scheduled: pl.DataFrame, for_each: list[str] | str, group_on_column: str
) -> pl.DataFrame:
    """
    Get grouped subframes containing grouped decision variables by those fields which are "for each" when used for
    constraint generation.

    Args:
        group_on_column: column to aggregate (either "is_scheduled_cp_var" or "is_scheduled_result"
        subset_scheduled: pl.Dataframe subset from `scheduled` to set ranges along axes to place constraint
        for_each: axis or axes to group by
    Returns:
        grouped pl.DataFrame

    Notes:
        Note any filtering should have happened before this.

        Somewhat cursed method to pile each group together. This returns subframes and "aggregates" the decision
        variables into a pile without actually doing anything to them. Long story short, the group_by elements are
        the "for each" groups and the non-mentioned ones are "for all." Note if you try to look at it, you just get
        errors.

    Examples:
        The 1:1:1 constraint is "for each resident, for each week, for all rotations, sum of all should be == 1
        for example, so for_each should receive `resident` and `week`. This means the `rotation` field is grouped.

    MAYBE I wonder if it could be done more transparently, like with .implode, but this works for now.
    """
    # TODO test the test
    assert (
        group_on_column in subset_scheduled.columns
    ), f"{group_on_column} not in {subset_scheduled.columns}"
    grouped = subset_scheduled.group_by(for_each).agg(pl.col(group_on_column))
    return grouped
