import polars as pl
from loguru import logger

import config
from data_io import compose_requirements_to_workers, convert_melted_to_block_schedule
from main import generate_complete_schedule


def test_starmap_constraints_minimal_case(minimal_case_setup):
    workers, rotations, weeks, requirements = minimal_case_setup
    workers_with_reqs = compose_requirements_to_workers(workers, requirements)
    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides=None, requests=None
    )

    assert starmap_verify_req_constraints(workers_with_reqs, weeks, solved_schedule)
    assert starmap_verify_rot_constraints(rotations, solved_schedule)


def test_min_contiguity_constraints(minimal_min_contiguity_case):
    workers, rotations, weeks, requirements = minimal_min_contiguity_case
    workers_with_reqs = compose_requirements_to_workers(workers, requirements)
    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides=None, requests=None
    )

    block = convert_melted_to_block_schedule(solved_schedule)

    with pl.Config(tbl_cols=-1):
        logger.trace(block)

    assert starmap_verify_req_constraints(workers_with_reqs, weeks, solved_schedule)
    assert starmap_verify_rot_constraints(rotations, solved_schedule)


def test_max_contiguity_constraints(minimal_max_contiguity_case):
    workers, rotations, weeks, requirements = minimal_max_contiguity_case
    workers_with_reqs = compose_requirements_to_workers(workers, requirements)
    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides=None, requests=None
    )

    assert starmap_verify_req_constraints(workers_with_reqs, weeks, solved_schedule)
    logger.debug(
        f"Requirement constraints verified across {len(workers_with_reqs)} workers and {len(solved_schedule)} variables."
    )
    assert starmap_verify_rot_constraints(rotations, solved_schedule)
    logger.debug(
        f"Rotation constraints verified across {len(rotations)} rotations and {len(solved_schedule)} variables."
    )

    block = convert_melted_to_block_schedule(solved_schedule)

    with pl.Config(tbl_cols=-1):
        logger.trace(block)


def starmap_verify_req_constraints(
    workers_with_reqs: pl.DataFrame, weeks: pl.DataFrame, solved_schedule: pl.DataFrame
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
                    case "min_contiguity":
                        if not verify_req_min_contiguity_constraint(
                            solved_schedule,
                            worker["name"],
                            req_body["fulfilled_by"],
                            req_body["constraints"]["min_contiguity"],
                        ):
                            return False
                    case "max_contiguity":
                        if not verify_req_max_contiguity_constraint(
                            solved_schedule,
                            worker["name"],
                            req_body["fulfilled_by"],
                            req_body["constraints"]["max_contiguity"],
                        ):
                            return False
                    case "prerequisite":
                        if not verify_req_prerequisite(
                            solved_schedule,
                            weeks,
                            worker=worker["name"],
                            affected_rotations=req_body["fulfilled_by"],
                            rots_meeting_prereqs=req_body["constraints"][
                                "prerequisite"
                            ]["rots_meeting_prereqs"],
                            prereq_weeks=req_body["constraints"]["prerequisite"][
                                "weeks"
                            ],
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


def verify_req_min_contiguity_constraint(
    solved_schedule: pl.DataFrame,
    worker: str,
    affected_rotations: list[str],
    min_contiguity: int,
) -> bool:
    """
    For each affected rotation, walk that worker's per-rotation assignments in chronological order and require every
    maximal run of scheduled weeks has length >= `min_contiguity`.

    :param solved_schedule:
    :param worker: 1 and only 1 worker
    :param affected_rotations: rotations for which THIS requirement demands contiguity
    :param min_contiguity:
    :return:
    """
    for rotation in affected_rotations:
        is_scheduled_weeks = (
            solved_schedule.filter(pl.col("name") == worker)
            .filter(pl.col("rotation") == rotation)
            .sort(by="monday_date")
            .select(config.CPMPY_RESULT_COLUMN)
            .to_series()
            .to_list()
        )

        run_length = 0
        for is_scheduled in is_scheduled_weeks:
            if is_scheduled:
                run_length += 1
            else:
                if 0 < run_length < min_contiguity:
                    return False
                run_length = 0

        if 0 < run_length < min_contiguity:
            return False

    return True


def verify_req_max_contiguity_constraint(
    solved_schedule: pl.DataFrame,
    worker: str,
    affected_rotations: list[str],
    max_contiguity: int,
) -> bool:
    """
    For each affected rotation, walk that worker's per-rotation assignments in chronological order and require every
    maximal run of scheduled weeks has length <= `max_contiguity`.

    :param solved_schedule:
    :param worker: 1 and only 1 worker
    :param affected_rotations: rotations for which THIS requirement demands contiguity
    :param max_contiguity:
    :return:
    """
    for rotation in affected_rotations:
        is_scheduled_weeks = (
            solved_schedule.filter(pl.col("name") == worker)
            .filter(pl.col("rotation") == rotation)
            .sort(by="monday_date")
            .select(config.CPMPY_RESULT_COLUMN)
            .to_series()
            .to_list()
        )

        run_length = 0
        for is_scheduled in is_scheduled_weeks:
            if is_scheduled:
                run_length += 1
            else:
                if run_length > max_contiguity:
                    return False
                run_length = 0

        if run_length > max_contiguity:
            return False

    return True


def verify_req_prerequisite(
    solved_schedule: pl.DataFrame,
    weeks: pl.DataFrame,
    worker: str,
    affected_rotations: list[str],
    rots_meeting_prereqs: list[str],
    prereq_weeks: int,
) -> bool:

    this_worker_schedule = solved_schedule.filter(pl.col("name") == worker)
    for rotation in affected_rotations:
        for week in weeks.iter_rows(named=True):
            rots_meeting_prereq_before_this_week = this_worker_schedule.filter(
                (pl.col("monday_date") < week["monday_date"])
                & (pl.col("rotation").is_in(rots_meeting_prereqs))
            )[config.CPMPY_RESULT_COLUMN].sum()

            this_week_is_sched_for_rot_with_prereqs = this_worker_schedule.filter(
                (pl.col("rotation") == rotation)
                & (pl.col("monday_date") == week["monday_date"])
            )[config.CPMPY_RESULT_COLUMN].item()

            if this_week_is_sched_for_rot_with_prereqs:
                assert rots_meeting_prereq_before_this_week >= prereq_weeks
    logger.warning("TODO: verify_req_prerequisite incomplete.")
    return True


def starmap_verify_rot_constraints(
    rotations: dict[str, dict], solved_schedule: pl.DataFrame
) -> bool:
    """
    Dispatcher for rotation constraints.

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


def test_minimal_prerequisites_case(minimal_prerequisites_case):
    workers, rotations, weeks, requirements = minimal_prerequisites_case

    workers_with_reqs = compose_requirements_to_workers(workers, requirements)

    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides=None, requests=None
    )

    block = convert_melted_to_block_schedule(solved_schedule)

    with pl.Config(tbl_cols=-1):
        logger.trace(block)

    assert starmap_verify_req_constraints(workers_with_reqs, weeks, solved_schedule)
    assert starmap_verify_rot_constraints(rotations, solved_schedule)
