import polars as pl

from config import config

cpmpy_variable_column = config.cpmpy_variable_column
cpmpy_result_column = config.cpmpy_result_column
default_solver = config.default_cpmpy_solver


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


def subset_scheduled_by(
    residents: pl.DataFrame | list[str],
    rotations: pl.DataFrame | list[str],
    weeks: pl.DataFrame | list[str],
    scheduled: pl.DataFrame,
) -> pl.DataFrame:
    """
    Subset the scheduled dataframe of cpmpy variables by supplied residents, rotations, and weeks.
    They can be supplied as str or as dataframes.

    Supply the full dataframe for any group to not perform any filtering by that element.

    Notes:
        You can always just filter manually. This is just a shorthand for a frequent operation.

    Args:
        residents:
        rotations:
        weeks:
        scheduled:

    Returns:
        Subset scheduled dataframe
    """
    if isinstance(residents, pl.DataFrame):
        resident_names = residents["full_name"].to_list()
    else:
        resident_names = residents

    if isinstance(rotations, pl.DataFrame):
        rotation_names = rotations["rotation"].to_list()
    else:
        rotation_names = rotations

    if isinstance(weeks, pl.DataFrame):
        week_dates = weeks["monday_date"].to_list()
    else:
        week_dates = weeks

    subset_scheduled = scheduled.filter(
        (pl.col("resident").is_in(resident_names))
        & (pl.col("rotation").is_in(rotation_names))
        & (pl.col("week").is_in(week_dates))
    )
    return subset_scheduled


def group_scheduled_df_by_for_each(
    subset_scheduled: pl.DataFrame,
    for_each_individual: list[str] | str,
    group_on_column: str,
) -> pl.DataFrame:
    """
    Get grouped subframes containing grouped decision variables by those fields which are "for each (individual)" when used for
    constraint generation. The returned grouped dataframe is thus siloed into groups which should be manipulated in iterated steps.

    Args:
        group_on_column: column to aggregate (either cpmpy_variable_column or cpmpy_result_column as found in config)
        subset_scheduled: pl.Dataframe subset from `scheduled` to set ranges along axes to place constraint
        for_each_individual: axis or axes to group by
    Returns:
        grouped pl.DataFrame

    Notes:
        Note any filtering should have happened before this as it will be hard to do now.

        I recognize this is essentially one line, but it's so syntactically weird I think it's worth leaving this way.

    Examples: The 1:1:1 constraint is "for each resident, for each week, for all rotations, sum of all should be ==
    1. In that case, for_each should receive `resident` and `week`. This means the `rotation` field is subject to
    constraint application and can then be processed in the next function.
    """
    assert (
        group_on_column in subset_scheduled.columns
    ), f"{group_on_column} not in {subset_scheduled.columns}"
    grouped = subset_scheduled.group_by(for_each_individual).agg(
        pl.col(group_on_column)
    )
    return grouped
