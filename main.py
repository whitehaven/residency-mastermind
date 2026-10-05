import sys

import cpmpy as cp
import polars as pl
from loguru import logger

import config
from constraints import (
    accumulate_req_constraints,
    accumulate_rotation_constraints,
    generate_every_worker_is_somewhere_constraints,
    generate_override_enforcement_constraints,
)
from data_io import (
    compose_requirements_to_workers,
    generate_pl_wrapped_boolvar,
    get_MUS_output,
)
from optimization import create_preferences_objective

logger.remove()
logger.add(sys.stderr, level=config.LOGGER_OUTPUT_LEVEL)
logger.add("logs/run_{time:YYYY-MM-DD_HH-mm-ss}.log", level="TRACE", rotation="10 MB")


def generate_complete_schedule(
    workers: pl.DataFrame,
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    requirement_sets: dict[str, dict],
    overrides: pl.DataFrame | None,
    preferences: pl.DataFrame | None,
) -> pl.DataFrame:
    model = cp.Model()

    scheduled = generate_pl_wrapped_boolvar(workers, rotations, weeks)

    workers_with_reqs = compose_requirements_to_workers(workers, requirement_sets)

    logger.warning(
        "No internal consistency checks are implemented. Errors will only be caught by failed indexing."
    )

    every_worker_is_somewhere_constraints = (
        generate_every_worker_is_somewhere_constraints(scheduled)
    )
    model += every_worker_is_somewhere_constraints
    logger.info(f"Added {len(every_worker_is_somewhere_constraints)=} constraints.")

    requirement_constraints = accumulate_req_constraints(
        workers_with_reqs, rotations, weeks, scheduled
    )
    model += requirement_constraints
    logger.info(f"Added {len(requirement_constraints)=} constraints.")

    rotations_constraints = accumulate_rotation_constraints(
        workers_with_reqs, rotations, weeks, scheduled
    )

    model += rotations_constraints
    logger.info(f"Added {len(rotations_constraints)=} constraints.")

    if overrides is not None:
        override_constraints = generate_override_enforcement_constraints(
            scheduled, overrides
        )
        model += override_constraints
        logger.info(f"Added {len(override_constraints)=} constraints.")
    else:
        logger.info("No override constraints specified.")

    if preferences is not None:
        preferences_objective = create_preferences_objective(scheduled, preferences)
        model.maximize(preferences_objective)
        logger.info("Added preferences objective.")
    else:
        logger.info("No preferences specified, solving for feasibility only.")

    is_feasible = model.solve(
        solver=config.DEFAULT_CPMPY_SOLVER,
        log_search_progress=config.VERBOSE_SOLVER_OUTPUT,
        time_limit=config.SOLVER_TIME_LIMIT,
    )

    if not is_feasible:
        logger.error(get_MUS_output(model))
        raise RuntimeError("Infeasible, MUS output to log.")

    logger.success("Feasibility confirmed.")
    solved_scheduled = scheduled.with_columns(
        pl.col(config.CPMPY_VARIABLE_COLUMN)
        .map_elements(lambda x: x.value(), return_dtype=pl.Boolean)
        .alias(config.CPMPY_RESULT_COLUMN)
    )

    return solved_scheduled
