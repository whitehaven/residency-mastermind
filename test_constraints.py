import cpmpy as cp
import polars as pl

from constraints import (
    require_one_rotation_per_resident_per_week,
    enforce_rotation_capacity_minimum,
    group_scheduled_df_by_for_each,
)
from data_io import generate_pl_wrapped_boolvar
from display import extract_solved_schedule
from testing_helpers import (
    grab_tester_weeks,
    grab_tester_rotations,
    grab_tester_residents,
)


def test_require_one_rotation_per_resident_per_week():
    test_scheduled = generate_pl_wrapped_boolvar(
        grab_tester_residents(),
        grab_tester_rotations(),
        grab_tester_weeks(),
    )
    test_constraints = require_one_rotation_per_resident_per_week(
        grab_tester_residents(),
        grab_tester_rotations(),
        grab_tester_weeks(),
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
    test_scheduled = generate_pl_wrapped_boolvar(
        residents=grab_tester_residents(),
        rotations=grab_tester_rotations(),
        weeks=grab_tester_weeks(),
    )
    test_constraints = enforce_rotation_capacity_minimum(
        residents=grab_tester_residents(),
        rotations=grab_tester_rotations(),
        weeks=grab_tester_weeks(),
        scheduled=test_scheduled,
    )
    model = cp.Model()
    model += test_constraints
    model.solve("ortools", log_search_progress=False)

    solved_schedule = extract_solved_schedule(test_scheduled)

    grouped = group_scheduled_df_by_for_each(
        solved_schedule,
        for_each=["rotation", "week"],
        group_on_column="is_scheduled_cp_var",
    )

    constraints = list()
    for group in grouped.iter_rows(named=True):
        decision_vars = group["is_scheduled_cp_var"]
        if decision_vars:
            rotation = grab_tester_rotations().filter(
                pl.col("rotation") == group["rotation"]
            )
            assert (
                sum(decision_vars)
                >= rotation.select(pl.col("minimum_residents_assigned")).item()
            ), f"sum decision_vars = {decision_vars} != minimum_residents_assigned for {rotation}"
