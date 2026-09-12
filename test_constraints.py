import sys

import pytest
from loguru import logger

from conftest import minimal_req_composition
from constraints import accumulate_req_constraints
from data_io import compose_requirements_to_workers
from test_data_io import generate_pl_wrapped_boolvar

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)


@pytest.mark.skip("incomplete")
def test_accumulate_req_constraints(minimal_case_setup, minimal_req_composition):
    workers, rotations, weeks, _requirements = minimal_case_setup
    logger.trace(
        f"loaded minimal test case: {workers.shape=}, {len(rotations)=}, {weeks.shape=}"
    )

    requirement_sets = minimal_req_composition
    logger.trace(f"loaded minimal requirement set: {len(requirement_sets)=}")

    workers_with_reqsets = compose_requirements_to_workers(workers, requirement_sets)
    logger.trace(f"generated individual reqsets: {workers_with_reqsets.shape=}")

    scheduled = generate_pl_wrapped_boolvar(workers_with_reqsets, rotations, weeks)
    logger.info(f"generated organized scheduled variables: {scheduled.shape=}")

    cumulative_constraints = accumulate_req_constraints(
        workers_with_reqsets, rotations, weeks, scheduled
    )

    assert isinstance(cumulative_constraints, list)
    logger.warning("TODO: test_enforce_requirement_constraints incomplete")


def test_generate_max_weeks_req_constraints():
    assert False


def test_generate_min_weeks_req_constraints():
    assert False
