import sys

import cpmpy as cp
import polars as pl
from loguru import logger

import config
from constraints import (
    accumulate_req_constraints,
    accumulate_rotation_constraints,
    generate_every_worker_is_somewhere_constraints,
)
from data_io import (
    compose_requirements_to_workers,
    generate_pl_wrapped_boolvar,
    get_MUS_output,
)

logger.remove()
logger.add(sys.stderr, level="TRACE")


def generate_complete_schedule(
    workers: pl.DataFrame,
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    requirement_sets: dict[str, dict],
    overrides: pl.DataFrame | None,
    requests: pl.DataFrame | None,
) -> pl.DataFrame:
    """
    inputs
        [later, assumes completed] read files
        [later] validation
        [x] generation of cpmpy variable df `scheduled`
        requirement sets composition
    constraints
        Requirement set enforcement (for each requirement group)
        overrides
    optimization
    results
        unsatisfiability diagnostics
        export

        :return: solved_schedule : pl.DataFrame := completed schedule, is `scheduled` above with additional column indicating solved bool for that coordinate
    """
    model = cp.Model()

    scheduled = generate_pl_wrapped_boolvar(workers, rotations, weeks)

    workers_with_reqs = compose_requirements_to_workers(workers, requirement_sets)

    every_worker_is_somewhere_constraints = (
        generate_every_worker_is_somewhere_constraints(scheduled)
    )
    model += every_worker_is_somewhere_constraints

    requirement_constraints = accumulate_req_constraints(
        workers_with_reqs, rotations, weeks, scheduled
    )
    model += requirement_constraints

    rotations_constraints = accumulate_rotation_constraints(
        workers_with_reqs, rotations, weeks, scheduled
    )

    model += rotations_constraints

    logger.warning(
        "TODO: Overrides functionality not implemented. Overrides will not be reflected in solutions nor unsatisfiability diagnostics."
    )
    logger.warning(
        "TODO: Preference optimization not implemented. Preferences will not be reflected in solutions nor unsatisfiability diagnostics."
    )

    is_feasible = model.solve(
        solver=config.DEFAULT_CPMPY_SOLVER,
        log_search_progress=config.VERBOSE_SOLVER_OUTPUT,
        time_limit=config.SOLVER_TIME_LIMIT,
    )

    if not is_feasible:
        logger.error(get_MUS_output(model))
        raise ValueError("Infeasible, MUS output to log.")

    logger.success("Feasibility confirmed.")
    solved_scheduled = scheduled.with_columns(
        pl.col(config.CPMPY_VARIABLE_COLUMN)
        .map_elements(lambda x: x.value(), return_dtype=pl.Boolean)
        .alias(config.CPMPY_RESULT_COLUMN)
    )

    return solved_scheduled
