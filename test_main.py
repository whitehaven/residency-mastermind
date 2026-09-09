import polars as pl

from main import generate_complete_schedule


def test_generate_complete_schedule_constraint_only_minimal_problem_size(
    minimal_case_setup,
):
    # TODO: minimal_case_setup's contents are unnested, don't allow req accumulation
    workers, rotations, weeks, _requirements = minimal_case_setup

    requirements = minimal_req_composition

    overrides = pl.DataFrame()
    requests = pl.DataFrame()

    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides, requests
    )

    raise NotImplementedError
