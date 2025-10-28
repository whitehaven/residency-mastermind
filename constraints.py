import warnings
from typing import Callable, LiteralString, Union

import box
import cpmpy as cp
import polars as pl

from config import config
from selection import group_scheduled_df_by_for_each, subset_scheduled_by

cpmpy_variable_column = config.cpmpy_variable_column
residents_primary_label = config.residents_primary_label
rotations_primary_label = config.rotations_primary_label

real_size_residents = pl.read_csv(config.testing_files.residents.real_size_seniors)
real_size_rotations = pl.read_csv(config.testing_files.rotations.real_size)
one_academic_year_weeks = pl.read_csv(
    config.testing_files.weeks.full_academic_year_2025_2026, try_parse_dates=True
)


def enforce_minimum_contiguity(
    constraint_weeks: int | LiteralString,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generate constraints that require that at least minimum_contiguity be respected.

    Prevents sequences of size lower than minimum contiguity. Any larger contiguity is then allowed.

    Notes:
        The base case is 1, which means rotation can be scheduled as singletons.
        No constraints are needed in that case. Null should be taken to mean 1.

        Only rotations with meaningful minimum_contiguity should be passed in.
        Filter for minimum_contiguity > 2 and not null.

    Args:
        constraint_weeks: python-box describing minimum contiguity constraint or "use_rotations_data" which will pull instead from the rotations dataframe. (This is not the intended final function.)
        residents: DataFrame of residents
        rotations: DataFrame of rotations with minimum_contiguous_weeks
        weeks: DataFrame of weeks
        scheduled: DataFrame with boolean variables for scheduling

    Returns:
        List of constraints preventing unacceptable contiguity patterns
    """
    cumulative_constraints = list()
    for rotation_dict in rotations.iter_rows(named=True):
        if constraint_weeks == "use_rotations_data":
            min_contiguity = rotation_dict["minimum_contiguous_weeks"]
            warnings.warn(
                "using rotations row data directly - this is not the intended use of this function outside of testing"
            )
        elif isinstance(constraint_weeks, int):
            min_contiguity = constraint_weeks
        else:
            raise ValueError(
                f"min_contiguity is {type(constraint_weeks)} which is not in int | str"
            )

        for resident_dict in residents.iter_rows(named=True):
            is_scheduled_for_res_on_rot = scheduled.filter(
                (pl.col("resident") == resident_dict[residents_primary_label])
                & (pl.col("rotation") == rotation_dict[rotations_primary_label])
            )

            schedule_vars = is_scheduled_for_res_on_rot[cpmpy_variable_column].to_list()
            for forbidden_length in range(1, min_contiguity):
                for start_idx in range(len(schedule_vars) - forbidden_length + 1):
                    constraint_against_sequence = prevent_isolated_sequence(
                        schedule_vars, start_idx, forbidden_length
                    )
                    cumulative_constraints.append(constraint_against_sequence)

    return cumulative_constraints


def prevent_isolated_sequence(
    variables: list[cp.core.BoolVal], start_idx: int, length: int
) -> cp.core.Comparison:
    """
    Create a constraint that prevents an isolated sequence of `length` of all True values at start_idx.

    An isolated sequence is one that:
    1. Has all variables in [start_idx, start_idx + length) set to True
    2. Is bounded by False values (or array boundaries)

    The constraint is violated if:
    - Left boundary is True (or doesn't exist)
    - All sequence variables are True
    - Right boundary is True (or doesn't exist)
    So we negate this: NOT(left_ok AND all_sequence_true AND right_ok)

    Args:
        variables: List of boolean variables
        start_idx: Starting index of the sequence to prevent
        length: Length of the sequence to prevent

    Returns:
        A constraint that evaluates to True when this pattern is NOT present

    References:
        This is based on an or-tools example under negated_bounded_span. This is a DeMorgan inversion of that.
        See https://github.com/google/or-tools/blob/stable/examples/python/shift_scheduling_sat.py.

    """
    sequence_vars = []

    # Left boundary: if not at start, the previous variable should be False
    if start_idx > 0:
        sequence_vars.append(~variables[start_idx - 1])

    # The sequence itself should not all be True
    sequence_vars.extend(variables[start_idx : start_idx + length])

    # Right boundary: if not at end, the next variable should be False
    if start_idx + length < len(variables):
        sequence_vars.append(~variables[start_idx + length])

    if len(sequence_vars) == length:
        # No boundaries, just prevent all variables in sequence being True
        return ~cp.all(sequence_vars)  # type: ignore
    else:
        # With boundaries: prevent the specific isolated pattern
        left_ok = sequence_vars[0] if start_idx > 0 else True
        sequence_true = cp.all(
            sequence_vars[
                1 if start_idx > 0 else 0 : 1 + length if start_idx > 0 else length
            ]
        )
        right_ok = sequence_vars[-1] if start_idx + length < len(variables) else True

        return ~(left_ok & sequence_true & right_ok)  # type: ignore


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
        for_each_individual=["resident", "week"],
        group_on_column=cpmpy_variable_column,
    )

    constraints = apply_constraint_to_groups(
        grouped, constraint_applicator=lambda group: cp.sum(group) == 1
    )

    return constraints


def enforce_minimum_rotation_weeks_per_resident(
    minimum_weeks: int,
    residents_subject_to_req: pl.DataFrame,
    rotations_fulfilling_req: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:

    subset_scheduled = subset_scheduled_by(
        residents_subject_to_req, rotations_fulfilling_req, weeks, scheduled
    )
    grouped = group_scheduled_df_by_for_each(
        subset_scheduled,
        for_each_individual=["resident"],
        group_on_column=cpmpy_variable_column,
    )
    constraints = apply_constraint_to_groups(
        grouped, constraint_applicator=lambda group: cp.sum(group) >= minimum_weeks
    )
    return constraints


def enforce_maximum_rotation_weeks_per_resident(
    maximum_weeks: int,
    residents_subject_to_req: pl.DataFrame,
    rotations_fulfilling_req: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:

    subset_scheduled = subset_scheduled_by(
        residents_subject_to_req, rotations_fulfilling_req, weeks, scheduled
    )
    grouped = group_scheduled_df_by_for_each(
        subset_scheduled,
        for_each_individual=["resident"],
        group_on_column=cpmpy_variable_column,
    )
    constraints = apply_constraint_to_groups(
        grouped, constraint_applicator=lambda group: cp.sum(group) <= maximum_weeks
    )
    return constraints


def enforce_exact_rotation_weeks_per_resident(
    exact_weeks: int,
    residents_subject_to_req: pl.DataFrame,
    rotations_fulfilling_req: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:

    subset_scheduled = subset_scheduled_by(
        residents_subject_to_req, rotations_fulfilling_req, weeks, scheduled
    )
    grouped = group_scheduled_df_by_for_each(
        subset_scheduled,
        for_each_individual=["resident"],
        group_on_column=cpmpy_variable_column,
    )

    constraints = apply_constraint_to_groups(
        grouped, constraint_applicator=lambda group: cp.sum(group) == exact_weeks
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
        for_each_individual=["rotation", "week"],
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
        for_each_individual=["rotation", "week"],
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


def enforce_requirement_constraints(
    requirements: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Enforce requirements fulfilled by rotations for all included residents over period of weeks, operating on dataframe containing cpmpy

    Notes:
        # MAYBE could benefit from combining all min/max/exact into one central function
    """
    cumulative_constraints = []
    for requirement_name, requirement_body in requirements.items():
        for constraint in requirement_body.constraints:
            match constraint.type:
                case "min_by_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    constraints = enforce_minimum_rotation_weeks_per_resident(
                        constraint.weeks,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        scheduled,
                    )
                case "max_by_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    constraints = enforce_maximum_rotation_weeks_per_resident(
                        constraint.weeks,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        scheduled,
                    )
                case "exact_by_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    constraints = enforce_exact_rotation_weeks_per_resident(
                        constraint.weeks,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        scheduled,
                    )
                case "min_contiguity_in_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    constraints = enforce_minimum_contiguity(
                        constraint.weeks,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        scheduled,
                    )
                case "max_contiguity_in_period":
                    raise NotImplementedError("Unclear if actually needed")
                case "prerequisite":
                    constraints = enforce_prerequisite(
                        prerequisite_constraint=constraint,
                        prerequisite_demander=requirement_name,
                        residents=residents,
                        rotations=rotations,
                        weeks=weeks,
                        scheduled=scheduled,
                    )
                case _:
                    raise LookupError(
                        f"{constraint.type=} is not a known requirement constraint type"
                    )
            cumulative_constraints.extend(constraints)
    return cumulative_constraints


def enforce_prerequisite(
    prerequisite_constraint: Union[box.Box | dict],
    prerequisite_demander: str,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    prereq_fulfillers = prerequisite_constraint.get("prerequisite")
    prereq_weeks_required = prerequisite_constraint.get("weeks")

    rotations_fulfilling_prereq = rotations.filter(
        pl.col("rotation").is_in(prereq_fulfillers)
    )

    skips = 0

    for resident_dict in residents.iter_rows(named=True):
        for week_dict in weeks.iter_rows(named=True):
            if week_dict["week"] < prereq_weeks_required:
                continue
            subset_scheduled_by(
                resident_dict[residents_primary_label],
                rotations.filter(pl.col("rotation").is_in(prereq_fulfillers)),
                weeks,
                scheduled,
            )

    # sum of all fulfillers weeks

    raise NotImplementedError("don't think the approach is correct yet")
