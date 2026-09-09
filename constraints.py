import sys

import cpmpy as cp
import polars as pl
from loguru import logger

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)


def enforce_requirement_constraints(
    workers_with_reqsets: pl.DataFrame,
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generates and accumulates all constraints which pertain to supplied workers, rotations, and weeks.

    :param workers_with_reqsets: workers df with assigned reqs columns
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

    raise NotImplementedError
