import sys

import cpmpy as cp
import polars as pl
from loguru import logger

import config

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)


def generate_requirement_constraints(
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

    cumulative_constraints = []

    for worker in workers_with_reqsets.iter_rows(named=True):
        for req_name, req_body in worker["req_set"].items():
            for constraint in req_body["constraints"]:
                match constraint:
                    case "max_weeks":
                        pass
                    case "min_weeks":
                        pass
                    case _:
                        raise NotImplementedError(
                            f"{constraint=} not a known constraint"
                        )

    logger.warning("note generate_requirement_constraints not completed and returns []")

    return cumulative_constraints


def generate_rotation_constraints(
    workers: pl.DataFrame,
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
                    pass
                case _:
                    raise NotImplementedError(
                        f"{constraint_name=} not a known constraint"
                    )

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

    Polars cannot `group_by(...).agg(list)` an `Object`-dtype column (the BoolVars),
    so each week's group is instead materialized with `partition_by("week")` and the
    Object column unwrapped with `.to_list()` to hand cpmpy a plain list to sum.

    :param scheduled:
    :param rotation:
    :param max_workers:
    :return:
    """
    cumu_constraints = []

    # TODO: need to lift out this functionality to reuse?

    scheduled_for_rotation = scheduled.filter(pl.col("rotation") == rotation)

    for week_group in scheduled_for_rotation.partition_by("week"):
        week_vars = week_group[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(week_vars) <= max_workers)

    return cumu_constraints
