import cpmpy as cp
import polars as pl

from config import read_config_file
from constraints import (
    require_one_rotation_per_resident_per_week,
    enforce_rotation_capacity_minimum,
    enforce_rotation_capacity_maximum,
)
from data_io import generate_pl_wrapped_boolvar
from display import extract_solved_schedule
from selection import group_scheduled_df_by_for_each

config = read_config_file()
cpmpy_variable_column = config["cpmpy_variable_column"]
cpmpy_result_column = config["cpmpy_result_column"]
default_solver = config["default_cpmpy_solver"]
tester_residents = pl.read_csv(
    config["testing_files"]["residents"]["real_size_seniors"]
)
tester_rotations = pl.read_csv(config["testing_files"]["rotations"]["real_size"])
tester_weeks = pl.read_csv(
    config["testing_files"]["weeks"]["full_year"], try_parse_dates=True
)


def test_require_one_rotation_per_resident_per_week() -> None:
    test_scheduled = generate_pl_wrapped_boolvar(
        tester_residents, tester_rotations, tester_weeks
    )
    test_constraints = require_one_rotation_per_resident_per_week(
        tester_residents,
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
    assert (
        len(
            solved_schedule.group_by(["resident", "week"])
            .sum()
            .filter(pl.col(cpmpy_result_column) != 1),
        )
        == 0
    ), "with test data, not every (resident -> week => all rotations) pairing has exactly 1 rotation set"
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
                max_residents_this_rotation = 0

            assert (
                sum(decision_vars) <= max_residents_this_rotation
            ), f"sum decision_vars = {decision_vars} != maximum_residents_assigned for {rotation}"
    return True
