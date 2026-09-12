import sys

import cpmpy as cp
import polars as pl
from loguru import logger

import config

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)


def accumulate_req_constraints(
    workers_with_reqsets: pl.DataFrame,
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generates and accumulates all constraints which pertain to supplied workers, rotations, and weeks.

    :param workers_with_reqsets: workers df with assigned reqs columns as ["req_set"]
    :param rotations:
    :param weeks:
    :param scheduled:
    :return:
    """

    cumu_constraints = []

    # TODO: probably should iterate workers by worker in workers_with_reqsets.partition_by("name")

    for worker in workers_with_reqsets.iter_rows(named=True):
        for req_name, req_body in worker["req_set"].items():
            for constraint in req_body["constraints"]:
                match constraint:
                    case "max_weeks":
                        cumu_constraints.extend(
                            generate_max_weeks_req_constraints(
                                scheduled.filter(pl.col("name") == worker["name"]),
                                fulfilling_rotations=req_body["fulfilled_by"],
                                max_weeks=req_body["constraints"]["max_weeks"],
                            )
                        )
                    case "min_weeks":
                        cumu_constraints.extend(
                            generate_min_weeks_req_constraints(
                                scheduled.filter(pl.col("name") == worker["name"]),
                                fulfilling_rotations=req_body["fulfilled_by"],
                                min_weeks=req_body["constraints"]["min_weeks"],
                            )
                        )
                    case "min_contiguity":
                        generate_min_contiguity_req_constraints(
                            scheduled,
                            affected_rotations=req_body["fulfilled_by"],
                            min_contiguity=req_body["constraints"]["min_contiguity"],
                        )
                    case _:
                        raise NotImplementedError(
                            f"{constraint=} not a known constraint"
                        )

    return cumu_constraints


def accumulate_rotation_constraints(
    workers: pl.DataFrame,  # TODO: not clear if needs to pass this since it applies to everyone universally
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generate rotation-specific constraints which are applied to all workers. These represent nonfungible locations.

    :param workers: pl.DataFrame with workers assigned. For convenience, can include reqs columns as ["req_set"] but not needed here.
    :param rotations:
    :param weeks:
    :param scheduled:
    :return:
    """
    cumu_constraints = []
    for rot_name, rot_body in rotations.items():
        for constraint_name, constraint_value in rot_body.items():
            match constraint_name:
                case "max_workers_assigned":
                    cumu_constraints.extend(
                        generate_rot_max_workers_constraints(
                            scheduled, rot_name, constraint_value
                        )
                    )
                case "min_workers_assigned":
                    cumu_constraints.extend(
                        generate_rot_min_workers_constraints(
                            scheduled, rot_name, constraint_value
                        )
                    )
                case _:
                    raise NotImplementedError(
                        f"{constraint_name=} not a known constraint"
                    )

    return cumu_constraints


def generate_every_worker_is_somewhere_constraints(
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generate constraints that require each worker is on exactly one rotation each week.


    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :return:
    """
    cumu_constraints = []
    for worker in scheduled.partition_by("name"):
        for week in worker.partition_by("monday_date"):
            all_rot_vars_this_worker_this_week = week[
                config.CPMPY_VARIABLE_COLUMN
            ].to_list()
            cumu_constraints.append(cp.sum(all_rot_vars_this_worker_this_week) == 1)

    return cumu_constraints


def generate_rot_max_workers_constraints(
    scheduled: pl.DataFrame,
    rotation: str,
    max_workers: int,
) -> list[cp.core.Comparison]:
    """
    For each week in `weeks`, require that no more than `max_workers_assigned`
    workers are scheduled to `rotation`. i.e. sum of that week's BoolVars for this
    rotation (one per worker) is <= `max_workers_assigned`.

    2026-09-09 Note: Polars cannot `group_by(...).agg(list)` an `Object`-dtype column (the BoolVars), so each week's
    group is instead materialized with `partition_by("week")` and the Object column unwrapped with `.to_list()` to
    hand cpmpy a plain list to sum. This was done in prior version (and used in `residency-mastermind` v0.9 and
    prior) but now deprecated, reflecting intention of group_by to be for calculation purposes only.

    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param rotation:
    :param max_workers:
    :return:
    """
    cumu_constraints = []

    # TODO: could this be generalized?

    scheduled_vars_this_rotation = scheduled.filter(pl.col("rotation") == rotation)

    for week_group in scheduled_vars_this_rotation.partition_by("week"):
        week_vars = week_group[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(week_vars) <= max_workers)

    return cumu_constraints


def generate_rot_min_workers_constraints(
    scheduled: pl.DataFrame, rotation: str, min_workers: int
) -> list[cp.core.Comparison]:
    """
    For each week in `weeks`, require that no fewer than `min`
    workers are scheduled to `rotation`. i.e. sum of that week's BoolVars for this
    rotation (one per worker) is <= `max_workers_assigned`.

    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param rotation:
    :param min_workers:
    :return:
    """
    cumu_constraints = []

    scheduled_vars_this_rotation = scheduled.filter(pl.col("rotation") == rotation)

    for week_group in scheduled_vars_this_rotation.partition_by("week"):
        week_vars = week_group[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(week_vars) >= min_workers)

    return cumu_constraints


def generate_min_weeks_req_constraints(
    scheduled: pl.DataFrame, fulfilling_rotations: list[str], min_weeks: int
) -> list[cp.core.Comparison]:
    """
    For each worker included, require that no fewer than `min` weeks are scheduled to `fulfilling rotations`.

    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param fulfilling_rotations:
    :param min_weeks:
    :return:
    """
    cumu_constraints = []

    scheduled_fulfilling_rotations = scheduled.filter(
        pl.col("rotation").is_in(fulfilling_rotations)
    )

    for worker in scheduled_fulfilling_rotations.partition_by("name"):
        this_workers_vars = worker[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(this_workers_vars) >= min_weeks)

    return cumu_constraints


def generate_max_weeks_req_constraints(
    scheduled: pl.DataFrame, fulfilling_rotations: list[str], max_weeks: int
) -> list[cp.core.Comparison]:
    """
    For each worker included, require that no more than `max` weeks are scheduled to `fulfilling rotations`.

    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param fulfilling_rotations:
    :param max_weeks:
    :return:
    """
    cumu_constraints = []

    scheduled_fulfilling_rotations = scheduled.filter(
        pl.col("rotation").is_in(fulfilling_rotations)
    )

    for worker in scheduled_fulfilling_rotations.partition_by("name"):
        this_workers_vars = worker[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(this_workers_vars) <= max_weeks)

    return cumu_constraints


def generate_min_contiguity_req_constraints(
    scheduled: pl.DataFrame, affected_rotations: list[str], min_contiguity: int
) -> list[cp.core.Comparison]:
    """
    Generate set of constraints that will require scheduled time on a rotation is always greater than or equal to `min_contiguity`.

    For example, if a requirement is that 4 weeks are spent on HS Rounding Senior rotations, any week that is scheduled must be part of a segment of 4 weeks.

    :param scheduled:
    :param affected_rotations:
    :param min_contiguity:
    :return:
    """
    pass
