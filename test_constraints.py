import warnings
from datetime import timedelta
from typing import Union

import box
import cpmpy as cp
import polars as pl
import pytest

from config import config
from constraints import (
    enforce_minimum_contiguity,
    enforce_requirement_constraints,
    enforce_rotation_capacity_maximum,
    enforce_rotation_capacity_minimum,
    require_one_rotation_per_resident_per_week,
)
from data_io import generate_pl_wrapped_boolvar
from display import extract_solved_schedule
from requirement_builder import (
    RequirementBuilder,
)
from selection import group_scheduled_df_by_for_each, subset_scheduled_by

cpmpy_variable_column = config.cpmpy_variable_column
cpmpy_result_column = config.cpmpy_result_column

real_size_residents = pl.read_csv(config.testing_files.residents.real_size_seniors)
real_size_rotations = pl.read_csv(config.testing_files.rotations.real_size)
one_academic_year_weeks = pl.read_csv(
    config.testing_files.weeks.full_academic_year_2025_2026, try_parse_dates=True
)

default_solver = config.default_cpmpy_solver


def test_require_one_rotation_per_resident_per_week() -> None:

    rotations = real_size_rotations
    weeks = one_academic_year_weeks

    residents = real_size_residents
    residents = residents.filter(pl.col("year").is_in((["R2", "R3"])))
    warnings.warn("filtering out extended-R3s")

    model = cp.Model()

    test_scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)
    test_constraints = require_one_rotation_per_resident_per_week(
        residents,
        rotations,
        weeks,
        scheduled=test_scheduled,
    )

    model += test_constraints
    is_feasible = model.solve("ortools", log_search_progress=False)
    if not is_feasible:
        raise ValueError("Infeasible")

    solved_schedule = extract_solved_schedule(test_scheduled)

    assert verify_one_rotation_per_resident_per_week(
        solved_schedule,
    ), "verify_one_rotation_per_resident_per_week == False"


def verify_one_rotation_per_resident_per_week(solved_schedule) -> bool:
    """
    Notes:
        This will be invalid if it shouldn't apply over the entire solved range.
    Args:
        solved_schedule: solved schedule♥

    Returns:
        bool: True if passes
    """
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        solved_schedule,
        for_each_individual=["resident", "week"],
        group_on_column=cpmpy_result_column,
    )
    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[cpmpy_result_column]

        assert sum(decision_vars) == 1, f"sum decision_vars = {decision_vars} != 1"

    return True


def test_enforce_rotation_capacity_minimum() -> None:
    residents = real_size_residents
    rotations = real_size_rotations
    weeks = one_academic_year_weeks

    rotations_with_minimum_residents = rotations.filter(
        pl.col("minimum_residents_assigned") > 0
    )

    test_scheduled = generate_pl_wrapped_boolvar(
        residents=residents,
        rotations=rotations_with_minimum_residents,
        weeks=weeks,
    )
    test_constraints = enforce_rotation_capacity_minimum(
        residents=residents,
        rotations=rotations_with_minimum_residents,
        weeks=weeks,
        scheduled=test_scheduled,
    )
    model = cp.Model()
    model += test_constraints
    model.solve(default_solver, log_search_progress=False)

    solved_schedule = extract_solved_schedule(test_scheduled)

    assert verify_enforce_rotation_capacity_minimum(
        rotations,
        solved_schedule,
    ), "verify_enforce_rotation_capacity_minimum == False"


def verify_enforce_rotation_capacity_minimum(rotations, solved_schedule) -> bool:
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        solved_schedule,
        for_each_individual=["rotation", "week"],
        group_on_column=cpmpy_result_column,
    )
    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[cpmpy_result_column]
        if decision_vars:
            rotation = rotations.filter(pl.col("rotation") == group_dict["rotation"])
            min_residents_this_rotation = rotation.select(
                pl.col("minimum_residents_assigned")
            ).item()
            if min_residents_this_rotation is None:
                min_residents_this_rotation = 0

            assert (
                sum(decision_vars) >= min_residents_this_rotation
            ), f"sum decision_vars = {decision_vars} != minimum_residents_assigned for {rotation}"
    return True


def test_enforce_rotation_capacity_maximum() -> None:
    residents = real_size_residents
    rotations = real_size_rotations
    weeks = one_academic_year_weeks

    rotations_with_minimum_residents = rotations.filter(
        pl.col("maximum_residents_assigned") > 0
    )

    test_scheduled = generate_pl_wrapped_boolvar(
        residents=residents,
        rotations=rotations_with_minimum_residents,
        weeks=weeks,
    )
    test_constraints = enforce_rotation_capacity_maximum(
        residents=residents,
        rotations=rotations_with_minimum_residents,
        weeks=weeks,
        scheduled=test_scheduled,
    )
    model = cp.Model()
    model += test_constraints
    model.solve(default_solver, log_search_progress=False)

    solved_schedule = extract_solved_schedule(test_scheduled)

    assert verify_enforce_rotation_capacity_maximum(
        rotations,
        solved_schedule,
    ), "verify_enforce_rotation_capacity_maximum == False"


def verify_enforce_rotation_capacity_maximum(rotations, solved_schedule) -> bool:
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        solved_schedule,
        for_each_individual=["rotation", "week"],
        group_on_column=cpmpy_result_column,
    )
    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[cpmpy_result_column]
        if decision_vars:
            rotation = rotations.filter(pl.col("rotation") == group_dict["rotation"])
            max_residents_this_rotation = rotation.select(
                pl.col("maximum_residents_assigned")
            ).item()
            if max_residents_this_rotation is None:
                assert (
                    False
                ), f"max_residents_this_rotation == {max_residents_this_rotation}? Doesn't make sense."

            assert (
                sum(decision_vars) <= max_residents_this_rotation
            ), f"sum decision_vars = {decision_vars} != maximum_residents_assigned for {rotation}"
    return True


def test_enforce_minimum_contiguity() -> None:
    residents = real_size_residents
    residents = residents.filter(pl.col("year").is_in(["R2", "R3"]))

    rotations = real_size_rotations
    weeks = one_academic_year_weeks

    scheduled = generate_pl_wrapped_boolvar(
        residents=residents,
        rotations=rotations,
        weeks=weeks,
    )

    model = cp.Model()

    rotations_with_minimum_contiguity = rotations.filter(
        (pl.col("minimum_contiguous_weeks") > 1)
        & (pl.col("minimum_contiguous_weeks").is_not_null())
    )
    contiguity_constraints = enforce_minimum_contiguity(
        "use_rotations_data",
        residents,
        rotations_with_minimum_contiguity,
        weeks,
        scheduled,
    )

    model += contiguity_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled=scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    is_feasible = model.solve(config.default_cpmpy_solver, log_search_progress=False)
    if not is_feasible:
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)
    assert verify_minimum_contiguity(
        "use_rotations_data",
        residents,
        rotations_with_minimum_contiguity,
        weeks,
        melted_solved_schedule,
    )


def verify_minimum_contiguity(
    constraint: Union[box.Box, str],
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    """
    Verify that the solved schedule respects minimum contiguity constraints.

    Args:
        constraint: python-box describing minimum contiguity constraint or "use_rotations_data" which will pull instead from the rotations dataframe. (This is not the intended final function.)
        rotations: DataFrame with rotations that have minimum_contiguous_weeks constraints
        solved_schedule: Melted schedule DataFrame with columns:
                        ['resident', 'rotation', 'week', 'scheduled'] where
                        'scheduled' is boolean indicating if resident is on rotation that week

    Returns:
        bool: True if all contiguity constraints are satisfied, False otherwise
    """
    for rotation_dict in rotations.iter_rows(named=True):

        rotation_name = rotation_dict[config.rotations_primary_label]
        if constraint == "use_rotations_data":
            min_contiguity = rotation_dict["minimum_contiguous_weeks"]
        else:
            min_contiguity = constraint.weeks  # type: ignore

        rotation_schedule = solved_schedule.filter(
            (pl.col("rotation") == rotation_name)
            & (pl.col(cpmpy_result_column) == True)  # noqa: E712
        )

        for resident_dict in residents.iter_rows(named=True):
            resident_rotation_schedule = rotation_schedule.filter(
                pl.col("resident") == resident_dict
            ).sort("week")

            scheduled_weeks = resident_rotation_schedule["week"].to_list()
            contiguous_blocks = find_contiguous_blocks(scheduled_weeks)

            for block in contiguous_blocks:
                if len(block) < min_contiguity:
                    print(
                        f"CONTIGUITY VIOLATION: Resident {resident_dict} on rotation {rotation_name}"
                    )
                    print(f"  Has block of length {len(block)}: {block}")
                    print(f"  But minimum contiguity is {min_contiguity}")
                    return False

    return True


def find_contiguous_blocks(week_list: list) -> list[list]:
    """
    Find all contiguous blocks in a list of week numbers/identifiers.

    Args:
        week_list: List of week identifiers (could be dates or week numbers, but in strange degraded state could be strings)

    Returns:
        List of lists, each containing a contiguous block of weeks
    """
    if not week_list:
        return []

    sorted_weeks = sorted(week_list)
    blocks = []
    current_block = [sorted_weeks[0]]

    for i in range(1, len(sorted_weeks)):
        if is_consecutive(sorted_weeks[i - 1], sorted_weeks[i]):
            current_block.append(sorted_weeks[i])
        else:
            # Start a new block
            blocks.append(current_block)
            current_block = [sorted_weeks[i]]

    blocks.append(current_block)

    return blocks


def is_consecutive(week1, week2) -> bool:
    """
    Check if week1 and week2 are consecutive and ordered week1 -> week2.

    Args:
        week1, week2: Week identifiers - should be datetime from weeks dataframe but could be integer week numbers (as judged from academic year start)

    Returns:
        bool: True if week2 immediately follows week1 (== 1 week later)
    """
    # If weeks are date-flavored objects
    if hasattr(week1, "year") and hasattr(week2, "year"):
        return week2 == week1 + timedelta(weeks=1)

    # If weeks are integers representing week numbers
    if isinstance(week1, int) and isinstance(week2, int):
        return week2 == week1 + 1

    # If weeks are strings, try conversion to integers assuming bad conversion (worst possible)
    try:
        return int(week2) == int(week1) + 1
    except (ValueError, TypeError):
        print("failed even to convert to string")

    # Fall back to string comparison (not ideal)
    return str(week2) == str(int(str(week1)) + 1)


@pytest.fixture
def sample_barely_fit_R2s_no_prereqs():
    residents = pl.DataFrame(
        {
            "full_name": ["First Guy", "Second Guy", "Third Guy", "Fourth Guy"],
            "year": ["R2", "R2", "R2", "R2"],
        }
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Green HS Senior", "Orange HS Senior", "Elective"],
            "category": ["HS Rounding Senior", "HS Rounding Senior", "Elective"],
            "required_role": ["Senior", "Senior", "Any"],
            "minimum_residents_assigned": [1, 1, 0],
            "maximum_residents_assigned": [1, 1, 10],
            "minimum_contiguous_weeks": [2, 2, None],
        }
    )
    weeks = one_academic_year_weeks.head(n=8)

    builder = RequirementBuilder()
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=[
                "Green HS Senior",
                "Orange HS Senior",
            ],
        )
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(12, ["R2"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()

    scheduled = generate_pl_wrapped_boolvar(
        residents,
        rotations,
        weeks,
    )
    return residents, rotations, weeks, current_requirements, scheduled


@pytest.fixture
def sample_simple_prerequisites_no_priors() -> (
    tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, box.Box, pl.DataFrame]
):
    residents = pl.DataFrame(
        {
            "full_name": ["First Guy", "Second Guy", "Third Guy"],
            "year": ["R2", "R2", "R2"],
        }
    )
    rotations = pl.DataFrame(
        {
            "rotation": [
                "Green HS Senior",
                "Orange HS Senior",
                "Elective",
                "Purple HS Senior",
            ],
            "category": [
                "HS Rounding Senior",
                "HS Rounding Senior",
                "Elective",
                "HS Admitting Senior",
            ],
            "required_role": ["Senior", "Senior", "Any", "Senior"],
            "minimum_residents_assigned": [0, 0, 0, 1],
            "maximum_residents_assigned": [1, 1, 10, 1],
            "minimum_contiguous_weeks": [2, 2, None, 2],
        }
    )
    weeks = one_academic_year_weeks.head(n=8)

    builder = RequirementBuilder()
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=[
                "Green HS Senior",
                "Orange HS Senior",
            ],
        )
        .min_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
        .after_prerequisite(
            prereq_fulfilling_rotations=["Purple HS Senior"],
            weeks_required=2,  # deliberately short so that the four can rotate through Elective to get out of the way
            resident_years=["R2"],
        )
    )
    (
        builder.add_requirement(
            name="HS Admitting Senior", fulfilled_by=["Purple HS Senior"]
        )
        .min_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(12, ["R2"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()

    scheduled = generate_pl_wrapped_boolvar(
        residents,
        rotations,
        weeks,
    )
    return residents, rotations, weeks, current_requirements, scheduled


def test_enforce_prerequisites_with_no_priors(
    sample_simple_prerequisites_no_priors,
):

    residents, rotations, weeks, current_requirements, scheduled = (
        sample_simple_prerequisites_no_priors
    )

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements, residents, rotations, weeks, scheduled
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    is_feasible = model.solve(config.default_cpmpy_solver, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"


def verify_prerequisite_met(
    constraint: Union[box.Box, dict],
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    raise NotImplementedError


def test_enforce_requirement_constraints_R2s_barely_fit(
    sample_barely_fit_R2s_no_prereqs,
):
    residents, rotations, weeks, current_requirements, scheduled = (
        sample_barely_fit_R2s_no_prereqs
    )

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements, residents, rotations, weeks, scheduled
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    is_feasible = model.solve(config.default_cpmpy_solver, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"


def verify_enforce_requirement_constraints(
    requirements: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
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
                    assert verify_minimum_week_constraint(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_minimum_week_requirement == False"

                case "max_by_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_maximum_week_constraint(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_maximum_week_requirement == False"

                case "exact_by_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_exact_week_constraint(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_exact_week_constraint failed"

                case "min_contiguity_in_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_minimum_contiguity(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_minimum_contiguity failed"

                case "prerequisite":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_prerequisite_met(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_exact_week_constraint failed"

                case "max_contiguity_in_period":
                    raise NotImplementedError("Unclear if actually needed")
                case _:
                    raise LookupError(
                        f"{constraint.type=} is not a known requirement constraint type"
                    )
    return True


def verify_minimum_week_constraint(
    constraint: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    relevant_schedule = subset_scheduled_by(
        residents, rotations, weeks, solved_schedule
    )
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        subset_scheduled=relevant_schedule,
        for_each_individual="resident",
        group_on_column=config.cpmpy_result_column,
    )

    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[cpmpy_result_column]

        if sum(decision_vars) < constraint.weeks:
            print(f"{sum(decision_vars)=} < {constraint=} !!!")
            return False
    return True


def verify_maximum_week_constraint(
    constraint: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    relevant_schedule = subset_scheduled_by(
        residents, rotations, weeks, solved_schedule
    )
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        subset_scheduled=relevant_schedule,
        for_each_individual="resident",
        group_on_column=config.cpmpy_result_column,
    )

    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[cpmpy_result_column]

        if sum(decision_vars) > constraint.weeks:
            print(f"{sum(decision_vars)=} > {constraint=} !!!")
            return False
    return True


def verify_exact_week_constraint(
    constraint: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    relevant_schedule = subset_scheduled_by(
        residents, rotations, weeks, solved_schedule
    )
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        subset_scheduled=relevant_schedule,
        for_each_individual="resident",
        group_on_column=config.cpmpy_result_column,
    )

    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[cpmpy_result_column]

        if sum(decision_vars) != constraint.weeks:
            print(f"{sum(decision_vars)=} != {constraint=} !!!")
            return False
    return True
