from typing import Callable

import cpmpy as cp
import polars as pl

from config import read_config_file

config = read_config_file()
cpmpy_variable_column = config["cpmpy_variable_column"]

#     TODO remake the contiguity functions
# def enforce_minimum_contiguity: <-
# def negated_bounded_span(superspan: pd.Series, start: int, length: int) -> list:
#     """Filters an isolated sub-sequence of variables assigned to True.
#
#     Extract the span of Boolean variables [start, start + length], negate them,
#     and if there is variables to the left/right of this span, surround the span by
#     them in non negated form.
#
#     Args:
#       superspan: a list of variables to extract the span from.
#       start: the start to the span.
#       length: the length of the span.
#
#     Returns:
#       a list of variables which conjunction will be false if the sub-list is
#       assigned to True, and correctly bounded by variables assigned to False,
#       or by the start or end of superspan.
#     """
#     sequence = []
#     # left border (start of superspan, or superspan[start - 1])
#     if start > 0:
#         sequence.append(superspan.iloc[start - 1])
#     for i in range(length):
#         sequence.append(~superspan.iloc[start + i])
#     # right border (end of superspan or superspan[start + length])
#     if start + length < len(superspan):
#         sequence.append(superspan.iloc[start + length])
#     return sequence

# TODO replace constraint utility functions
# def force_value
# def forbid_ineligible_rotations


def require_one_rotation_per_resident_per_week(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list:
    """
    Generate constraints that require exactly one True at every resident:rotation:week intersection.

    Can be subset from the base data imported early on.

    For example, a super-R3 who was out on maternity leave can be set to a limited range of weeks after being excluded
    from the main body of residents.

    Args:
        residents: df of residents - can be subset
        rotations:  df of weeks - can be subset
        weeks:  df of weeks - can be subset
        scheduled:  df of residents - can be subset

    Returns:
        list[constraints] that should force a solution which requires exactly one True at every resident:rotation:week intersection.
    """

    subset_scheduled = subset_scheduled_by(residents, rotations, weeks, scheduled)

    grouped = group_scheduled_df_by_for_each(
        subset_scheduled,
        for_each=["resident", "week"],
        group_on_column=cpmpy_variable_column,
    )

    constraints = apply_literal_constraint_to_groups(
        grouped, constraint_applicator=lambda group: cp.sum(group) == 1
    )

    return constraints


def apply_literal_constraint_to_groups(
    grouped: pl.DataFrame, constraint_applicator: Callable
) -> list:
    """

    Args:
        grouped: pl.DataFrame group_by'd by
        constraint_applicator: Callable that operates on a list() of cpmpy.BoolVar and returns a cpmpy.Comparison

    Returns:
        list[cpmpy.Comparison]
    """
    constraints = list()
    for group in grouped.iter_rows(named=True):
        decision_vars = group[cpmpy_variable_column]
        if decision_vars:
            constraints.append(constraint_applicator(decision_vars))
    return constraints


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


def enforce_requirement_constraints(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list:
    for resident in residents.iter_rows(named=True):
        pass
    return []  # TODO incomplete


def enforce_rotation_capacity_minimum(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list:
    """
    Set minimum residents on each rotation, equivalent to "resident-staffed."

    Returns: list[constraints]

    """
    # TODO testing

    rotations_with_minimum_residents = rotations.filter(
        pl.col("minimum_residents_assigned") > 0
    )

    subset_scheduled = subset_scheduled_by(
        residents, rotations_with_minimum_residents, weeks, scheduled
    )
    grouped = group_scheduled_df_by_for_each(
        subset_scheduled,
        for_each=["rotation", "week"],
        group_on_column=cpmpy_variable_column,
    )

    constraints = list()
    for group_dict in grouped.iter_rows(named=True):
        decision_vars = group_dict[cpmpy_variable_column]
        if decision_vars:
            rotation = rotations_with_minimum_residents.filter(
                pl.col("rotation") == group_dict["rotation"]
            )
            constraints.append(
                cp.sum(decision_vars)
                >= rotation.select(pl.col("minimum_residents_assigned")).item()
            )
    return constraints


if __name__ == "__main__":
    pass
