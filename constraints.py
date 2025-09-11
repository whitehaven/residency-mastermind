from typing import Callable

import box
import cpmpy as cp
import polars as pl

from selection import subset_scheduled_by, group_scheduled_df_by_for_each

config = box.box_from_file("config.yaml")
cpmpy_variable_column = config.cpmpy_variable_column
residents_primary_label = config.residents_primary_label
rotations_primary_label = config.rotations_primary_label


#     TODO remake the contiguity functions
def negated_bounded_span(
    superspan: list[cp.core.BoolVal], starting_idx: int, length: int
) -> list[cp.core.BoolVal]:
    """
    Generate negated series which would return false if it matches an underlying sequence of BoolVals. A list of these series is splayed out over every possible place that sequence could occur.

    In conjunction ("and") / Union, this returns False - this establishes there are no sequences of `length`
    contiguity. This must be done for each unacceptable length (e.g., minimum_contiguity = 2 => exclude 1;
    minimum_contiguity = 3 => exclude 1, 2)

    Original documentation: "Filters an isolated sub-sequence of variables assigned to True.

    Extract the span of Boolean variables [start, start + length]
    and if there is variables to the left/right of this span, surround the span by
    them in non-negated form."

    Args:
      superspan: a list of variables to extract the span from.
      starting_idx: the start to the span.
      length: the length of the span to extract

    Returns:
      Original documentation: "a list of variables which conjunction will be false if the sub-list is
      assigned to True, and correctly bounded by variables assigned to False,
      or by the start or end of works."

      Adapted (and negated) from or-tools examples repository, see https://raw.githubusercontent.com/google/or-tools/9b77015d9d7162b560b9e772c06ff262d2780844/examples/python/shift_scheduling_sat.py
    """
    sequence = []
    # left border (start of superspan, or superspan[start - 1])
    if starting_idx > 0:
        sequence.append(superspan[starting_idx - 1])
    for i in range(length):
        sequence.append(~superspan[starting_idx + i])
    # right border (end of superspan or superspan[start + length])
    if starting_idx + length < len(superspan):
        sequence.append(superspan[starting_idx + length])
    return sequence


def enforce_minimum_contiguity(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generate constraints that require that at least minimum_contiguity be respected.

    Only rotations with meaningful minimum_contiguity should be passed in.  Filter for minimum_contiguity > 2 and not null.

    Notes:
        The base case is 1, which means rotation can be scheduled at singletons. No constraints are needed in that case. Null should be taken to mean 1.

    Args:
        residents:
        rotations:
        weeks:
        scheduled:

    Returns:
        cumulative_constraints: list[cp.core.Comparison]: List of comparisons which will be or statements of variables for every possible
    """
    rotations_with_min_contig = rotations.filter(
        ~(pl.col("minimum_contiguous_weeks") <= 1)
        | ~(pl.col("minimum_contiguous_weeks").is_null())
    )

    cumulative_constraints = list()
    for rotation_dict in rotations_with_min_contig.iter_rows(named=True):
        constraints_on_this_rotation = list()
        for resident_dict in residents.iter_rows(named=True):
            is_scheduled_for_res_on_rot = scheduled.filter(
                (pl.col("resident") == resident_dict[residents_primary_label])
                & (pl.col("rotation") == rotation_dict[rotations_primary_label])
            )
            min_contiguity = rotation_dict["minimum_contiguous_weeks"]

            for contiguity_n in range(1, min_contiguity):
                for start_wk_idx in range(
                    len(is_scheduled_for_res_on_rot) - contiguity_n + 1
                ):
                    nbs = negated_bounded_span(
                        is_scheduled_for_res_on_rot[cpmpy_variable_column].to_list(),
                        start_wk_idx,
                        contiguity_n,
                    )

                    constraints_on_this_rotation.append(cp.all(nbs))
                # note skipped collection list here - no need to nest, the innermost one here will get them all by rotation with all residents mixed in
        cumulative_constraints.append(cp.sum(constraints_on_this_rotation) == 0)
    return cumulative_constraints


# TODO replace constraint utility functions
# def force_value
# def forbid_ineligible_rotations


def require_one_rotation_per_resident_per_week(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
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

    constraints = apply_constraint_to_groups(
        grouped, constraint_applicator=lambda group: cp.sum(group) == 1
    )

    return constraints


def apply_constraint_to_groups(
    grouped: pl.DataFrame, constraint_applicator: Callable
) -> list[cp.core.Comparison]:
    """
    Apply constraint function over aggregated constraint variables.
    Args:
        grouped: pl.DataFrame group_by'd into groups which will have constraint applied across them
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
) -> list[cp.core.Comparison]:
    """
    Set minimum residents on each rotation, equivalent to "resident-staffed."

    Returns: list[constraints]

    """
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


def enforce_rotation_capacity_maximum(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Set maximum residents on each rotation.

    Returns: list[constraints]

    """
    # TODO  should not handle filter here
    rotations_with_maximum_residents = rotations.filter(
        pl.col("maximum_residents_assigned") > 0
    )

    subset_scheduled = subset_scheduled_by(
        residents, rotations_with_maximum_residents, weeks, scheduled
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
            rotation = rotations_with_maximum_residents.filter(
                pl.col("rotation") == group_dict["rotation"]
            )
            constraints.append(
                cp.sum(decision_vars)
                <= rotation.select(pl.col("maximum_residents_assigned")).item()
            )
    return constraints


if __name__ == "__main__":
    pass
