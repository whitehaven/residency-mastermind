import sys

import polars as pl
import pytest
from loguru import logger

import config
from conftest import minimal_req_composition
from constraints import accumulate_req_constraints
from data_io import compose_requirements_to_workers
from main import generate_complete_schedule
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


def test_generate_max_weeks_req_constraints(minimal_case_setup):
    workers, _rotations, weeks, _requirements = minimal_case_setup

    rotations = {
        "Green HS Senior": {
            "max_workers_assigned": 1,
        },
        "Orange HS Senior": {
            "max_workers_assigned": 1,
        },
        "Vacation": {"max_workers_assigned": 2},
    }

    requirements = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {"max_weeks": 2},
                "fulfilled_by": [
                    "Green HS Senior",
                    "Orange HS Senior",
                ],
            },
            "Vacation": {"constraints": {"max_weeks": 3}, "fulfilled_by": ["Vacation"]},
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }

    workers_with_reqs = compose_requirements_to_workers(workers, requirements)

    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides=None, requests=None
    )

    assert starmap_verify_req_constraints(workers_with_reqs, solved_schedule)
    assert starmap_verify_rot_constraints(rotations, solved_schedule)


def starmap_verify_req_constraints(
    workers_with_reqs: pl.DataFrame, solved_schedule: pl.DataFrame
):
    for worker in workers_with_reqs.iter_rows(named=True):
        for req_name, req_body in worker["req_set"].items():
            for constraint in req_body["constraints"]:
                match constraint:
                    case "max_weeks":
                        if not verify_req_max_weeks_constraint(
                            solved_schedule,
                            worker["name"],
                            req_body["fulfilled_by"],
                            req_body["constraints"]["max_weeks"],
                        ):
                            return False
                    case "min_weeks":
                        if not verify_req_min_weeks_constraint(
                            solved_schedule,
                            worker["name"],
                            req_body["fulfilled_by"],
                            req_body["constraints"]["min_weeks"],
                        ):
                            return False
                    case _:
                        raise NotImplementedError(
                            f"{constraint=} not a known constraint"
                        )
    return True


def verify_req_max_weeks_constraint(
    solved_schedule: pl.DataFrame,
    worker: str,
    fulfilling_rotations: list[str],
    max_weeks: int,
):
    """
    Verify sum of post-solve cpmpy True max_weeks for this worker and set of fulfilling rotations.

    This is fully unlooped - the loop through workers, etc. all come from the caller, i.e., starmap_verify_req_constraints.

    2026-09-12: I tried to inline this, but it was unreadable and disgusting. I'll spend a stack frame to keep it manageable.

    :param solved_schedule:
    :param worker: 1 and only 1 worker
    :param fulfilling_rotations: rotations that count for THIS requirement
    :param max_weeks:
    :return:
    """

    weeks_scheduled = (
        solved_schedule.filter(pl.col("name") == worker)
        .filter(pl.col("rotation").is_in(fulfilling_rotations))
        .select(config.CPMPY_RESULT_COLUMN)
        .sum()
        .item()
    )

    constraint_met = weeks_scheduled <= max_weeks

    return constraint_met


def verify_req_min_weeks_constraint(
    solved_schedule: pl.DataFrame,
    worker: str,
    fulfilling_rotations: list[str],
    min_weeks: int,
) -> bool:
    weeks_scheduled = (
        solved_schedule.filter(pl.col("name") == worker)
        .filter(pl.col("rotation").is_in(fulfilling_rotations))
        .select(config.CPMPY_RESULT_COLUMN)
        .sum()
        .item()
    )

    constraint_met = weeks_scheduled >= min_weeks

    return constraint_met


def starmap_verify_rot_constraints(
    rotations: dict[str, dict], solved_schedule: pl.DataFrame
) -> bool:
    """

    :param solved_schedule:
    :param rotations:
    :return:
    """
    for rot_name, rot_body in rotations.items():
        for constraint_name, constraint_body in rot_body.items():
            for week_schedule in solved_schedule.partition_by("monday_date"):
                match constraint_name:
                    case "max_workers_assigned":
                        if not verify_rot_max_workers_constraint(
                            week_schedule, rot_name, rot_body["max_workers_assigned"]
                        ):
                            return False
                    case "min_workers_assigned":
                        if not verify_rot_min_workers_constraint(
                            week_schedule, rot_name, rot_body["min_workers_assigned"]
                        ):
                            return False
                    case _:
                        raise NotImplementedError(
                            f"{constraint_name=} not a known constraint"
                        )
    return True
    #
    # for rot_name, rot_body in rotations.items():
    #     for constraint_name, constraint_body in rot_body.items():
    #         match constraint_name:
    #             case "max_workers_assigned":
    #                 if not verify_rot_max_workers_constraint(
    #                     solved_schedule, rot_name, rot_body["max_workers_assigned"]
    #                 ):
    #                     return False
    #             case "min_workers_assigned":
    #                 if not verify_rot_min_workers_constraint(
    #                     solved_schedule, rot_name, rot_body["min_workers_assigned"]
    #                 ):
    #                     return False
    #             case _:
    #                 raise NotImplementedError(
    #                     f"{constraint_name=} not a known constraint"
    #                 )


def verify_rot_max_workers_constraint(
    solved_schedule: pl.DataFrame, rotation: str, max_workers: int
) -> bool:
    weeks_scheduled = (
        solved_schedule.filter(pl.col("rotation") == rotation)
        .select(config.CPMPY_RESULT_COLUMN)
        .sum()
        .item()
    )

    constraint_met = weeks_scheduled <= max_workers

    return constraint_met


def verify_rot_min_workers_constraint(
    solved_schedule: pl.DataFrame, rotation: str, min_workers: int
) -> bool:
    weeks_scheduled = (
        solved_schedule.filter(pl.col("rotation") == rotation)
        .select(config.CPMPY_RESULT_COLUMN)
        .sum()
        .item()
    )

    constraint_met = weeks_scheduled >= min_workers

    return constraint_met
