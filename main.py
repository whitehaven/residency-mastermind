import polars as pl

from data_io import compose_requirements_to_workers, generate_pl_wrapped_boolvar


def generate_complete_schedule(
    workers: pl.DataFrame,
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    requirement_sets: dict[str, dict],
    overrides: pl.DataFrame,
    requests: pl.DataFrame,
):
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
    """
    scheduled = generate_pl_wrapped_boolvar(workers, rotations, weeks)

    workers_with_requirements = compose_requirements_to_workers(
        workers, requirement_sets
    )
