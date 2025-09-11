import box
import cpmpy as cp
import polars as pl

from constraints import (
    require_one_rotation_per_resident_per_week,
    enforce_rotation_capacity_minimum,
    enforce_rotation_capacity_maximum,
    enforce_minimum_contiguity,
)
from data_io import generate_pl_wrapped_boolvar
from display import extract_solved_schedule, convert_melted_to_block_schedule
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

    assert len(contiguity_constraints) == len(
        rotations_with_minimum_contiguity
    ), f"{len(contiguity_constraints)} != {len(rotations_with_minimum_contiguity)}, but should"
    assert all(
        [
            isinstance(constraint, cp.core.Comparison)
            for constraint in contiguity_constraints
        ]
    ), "not all returned constraint elements are cp.core.Comparison"

    model += contiguity_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled=scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)

    model.solve(default_solver, log_search_progress=False)

    melted_solved_schedule = extract_solved_schedule(scheduled)

    block_schedule = convert_melted_to_block_schedule(melted_solved_schedule)
    block_schedule.write_csv("contig_block.csv")
    assert verify_minimum_contiguity(
        rotations_with_minimum_contiguity, solved_schedule=melted_solved_schedule
    )


def verify_minimum_contiguity(rotations, solved_schedule) -> bool:
    return False
