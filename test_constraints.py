import cpmpy as cp
import polars as pl

from constraints import (
    require_one_rotation_per_resident_per_week,
    enforce_rotation_capacity_minimum,
    group_scheduled_df_by_for_each,
    )
from data_io import generate_pl_wrapped_boolvar
from display import extract_solved_schedule
from testing_helpers import tester_residents, tester_rotations, tester_weeks


def test_require_one_rotation_per_resident_per_week():
    test_scheduled = generate_pl_wrapped_boolvar(
        tester_residents, tester_rotations, tester_weeks
    )
    test_constraints = require_one_rotation_per_resident_per_week(
        tester_residents,
        tester_rotations,
        tester_weeks,
        scheduled=test_scheduled,
    )
    assert len(test_constraints) == 18

    model = cp.Model()
    model += test_constraints
    model.solve("ortools", log_search_progress=False)

    solved_schedule = extract_solved_schedule(test_scheduled)

    assert (
        len(
            solved_schedule.group_by(["resident", "week"])
            .sum()
            .filter(pl.col("is_scheduled_result") != 1)
        )
        == 0
    ), "with test data, not every (resident -> week => all rotations) pairing has exactly 1 rotation set"



def test_enforce_rotation_capacity_minimum():

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
    model.solve("ortools", log_search_progress=False)

    solved_schedule = extract_solved_schedule(test_scheduled)

    return verify_enforce_rotation_capacity_minimum(rotations, solved_schedule)


def verify_enforce_rotation_capacity_minimum(rotations, solved_schedule) -> bool:
    grouped_solved_schedule = group_scheduled_df_by_for_each(
            solved_schedule, for_each=["rotation", "week"], group_on_column="is_scheduled_result", )
    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict["is_scheduled_result"]
        if decision_vars:
            rotation = rotations.filter(pl.col("rotation") == group_dict["rotation"])
            assert (sum(decision_vars) >= rotation.select(pl.col("minimum_residents_assigned")).item()
            ), f"sum decision_vars = {decision_vars} != minimum_residents_assigned for {rotation}"
    return True
