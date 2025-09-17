from datetime import timedelta

import box
import cpmpy as cp
import polars as pl
import pytest

from constraints import (
    require_one_rotation_per_resident_per_week,
    enforce_rotation_capacity_minimum,
    enforce_rotation_capacity_maximum,
    enforce_minimum_contiguity,
    enforce_requirement_constraints,
    enforce_maximum_contiguity,
)
from data_io import generate_pl_wrapped_boolvar
from display import extract_solved_schedule
from selection import group_scheduled_df_by_for_each

config = box.box_from_file("config.yaml")
cpmpy_variable_column = config.cpmpy_variable_column
cpmpy_result_column = config.cpmpy_result_column

tester_residents = pl.read_csv(config.testing_files.residents.real_size_seniors)
tester_rotations = pl.read_csv(config.testing_files.rotations.real_size)
tester_weeks = pl.read_csv(
    config.testing_files.weeks.full_academic_year_2025_2026, try_parse_dates=True
)

default_solver = config.default_cpmpy_solver


def test_require_one_rotation_per_resident_per_week() -> None:

    normal_scheduled_tester_residents = tester_residents.filter(
        pl.col("year").is_in((["R2", "R3"]))
    )

    test_scheduled = generate_pl_wrapped_boolvar(
        normal_scheduled_tester_residents, tester_rotations, tester_weeks
    )
    test_constraints = require_one_rotation_per_resident_per_week(
        normal_scheduled_tester_residents,
        tester_rotations,
        tester_weeks,
        scheduled=test_scheduled,
    )

    model = cp.Model()
    model += test_constraints
    model.solve(default_solver, log_search_progress=False)

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
        for_each=["resident", "week"],
        group_on_column=cpmpy_result_column,
    )
    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[cpmpy_result_column]

        assert sum(decision_vars) == 1, f"sum decision_vars = {decision_vars} != 1"

    return True


def test_enforce_rotation_capacity_minimum() -> None:

    residents = tester_residents
    rotations = tester_rotations
    weeks = tester_weeks

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
        for_each=["rotation", "week"],
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

    residents = tester_residents
    rotations = tester_rotations
    weeks = tester_weeks

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
        for_each=["rotation", "week"],
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
    # TODO complete test
    residents = tester_residents
    residents = residents.filter(pl.col("year").is_in(["R2", "R3"]))
    rotations = tester_rotations
    weeks = tester_weeks

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
        rotations_with_minimum_contiguity, solved_schedule=melted_solved_schedule
    )


def verify_minimum_contiguity(rotations, solved_schedule) -> bool:
    """
    Verify that the solved schedule respects minimum contiguity constraints.

    Args:
        rotations: DataFrame with rotations that have minimum_contiguous_weeks constraints
        solved_schedule: Melted schedule DataFrame with columns:
                        ['resident', 'rotation', 'week', 'scheduled'] where
                        'scheduled' is boolean indicating if resident is on rotation that week

    Returns:
        bool: True if all contiguity constraints are satisfied, False otherwise
    """
    for rotation_dict in rotations.iter_rows(named=True):

        if rotation_dict["minimum_contiguous_weeks"] is None:
            continue

        rotation_name = rotation_dict[config.rotations_primary_label]
        min_contiguity = rotation_dict["minimum_contiguous_weeks"]

        # Get all residents assigned (cpmpy_result_column==True) to this rotation
        rotation_schedule = solved_schedule.filter(
            (pl.col("rotation") == rotation_name)
            & (pl.col(cpmpy_result_column) == True)
        )

        for resident_name in rotation_schedule["resident"].unique():
            resident_rotation_schedule = rotation_schedule.filter(
                pl.col("resident") == resident_name
            ).sort("week")

            if len(resident_rotation_schedule) == 0:
                raise RuntimeError(
                    f"{len(resident_rotation_schedule)=}, should only be == 0  following filter operations"
                )

            scheduled_weeks = resident_rotation_schedule["week"].to_list()
            contiguous_blocks = find_contiguous_blocks(scheduled_weeks)

            for block in contiguous_blocks:
                if len(block) < min_contiguity:
                    print(
                        f"CONTIGUITY VIOLATION: Resident {resident_name} on rotation {rotation_name}"
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


@pytest.mark.xfail
def test_enforce_requirement_constraints():
    residents = tester_residents
    residents = residents.filter(
        pl.col("year").is_in(["R2", "R3"])
    )  # TODO again, note filtered to exclude extended-R3s
    rotations = tester_rotations
    weeks = tester_weeks
    scheduled = generate_pl_wrapped_boolvar(
        residents=residents,
        rotations=rotations,
        weeks=weeks,
    )
    current_requirements = box.box_from_file("requirements.yaml")
    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        scheduled,
    )
    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )

    is_feasible = model.solve(config.default_cpmpy_solver, log_search_progress=False)
    if not is_feasible:
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
    current_requirements,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    return False


@pytest.mark.xfail
def test_enforce_maximum_contiguity():
    residents = tester_residents
    residents = residents.filter(pl.col("year").is_in(["R2", "R3"]))
    rotations = tester_rotations
    weeks = tester_weeks

    scheduled = generate_pl_wrapped_boolvar(
        residents=residents,
        rotations=rotations,
        weeks=weeks,
    )

    rotations_with_max_contiguity = rotations.filter(
        pl.col("max_contiguous_weeks").is_not_null()
    )
    enforce_maximum_contiguity(
        residents, rotations_with_max_contiguity, weeks, scheduled
    )

    assert verify_enforce_maximum_contiguity(
        residents, rotations, weeks, scheduled
    ), "verify_enforce_maximum_contiguity failed"


def verify_enforce_maximum_contiguity(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    # TODO watch out, passing entire rotations df (maybe)
    return False
