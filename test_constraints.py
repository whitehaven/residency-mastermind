from constraints import require_one_rotation_per_resident_per_week
from data_io import generate_pl_wrapped_boolvar
from testing_helpers import (
    grab_tester_weeks,
    grab_tester_rotations,
    grab_tester_residents,
)


def test_require_one_rotation_per_resident_per_week():
    scheduled = generate_pl_wrapped_boolvar(
        grab_tester_residents(),
        grab_tester_rotations(),
        grab_tester_weeks(),
    )
    test_constraints = require_one_rotation_per_resident_per_week(
        grab_tester_residents(),
        grab_tester_rotations(),
        grab_tester_weeks(),
        scheduled=scheduled,
    )
    # TODO test with tiny test cp.Model
    assert len(test_constraints) == 18
