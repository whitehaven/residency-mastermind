import cpmpy as cp
import polars as pl

from constraints import require_one_rotation_per_resident_per_week
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
