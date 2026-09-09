import cpmpy as cp
import polars as pl

import config
from constraints import generate_requirement_constraints, generate_rotation_constraints
from data_io import compose_requirements_to_workers, generate_pl_wrapped_boolvar


def generate_complete_schedule(
    workers: pl.DataFrame,
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    requirement_sets: dict[str, dict],
    overrides: pl.DataFrame,
    requests: pl.DataFrame,
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
    scheduled = generate_pl_wrapped_boolvar(workers, rotations, weeks)

    workers_with_requirements = compose_requirements_to_workers(
        workers, requirement_sets
    )

    model = cp.Model()

    requirement_constraints = generate_requirement_constraints(
        workers_with_requirements, rotations, weeks, scheduled
    )
    model += requirement_constraints

    rotations_constraints = generate_rotation_constraints(
        workers_with_requirements, rotations, weeks, scheduled
    )

    model += rotations_constraints

    is_feasible = model.solve(
        solver=config.DEFAULT_CPMPY_SOLVER,
        log_search_progress=config.VERBOSE_SOLVER_OUTPUT,
        time_limit=config.SOLVER_TIME_LIMIT,
    )

    if not is_feasible:
        # min_unsat_result = get_MUS(model)
        # print(min_unsat_result)
        raise ValueError("Infeasible")
