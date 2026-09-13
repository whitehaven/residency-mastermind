import polars as pl
from loguru import logger

from data_io import convert_melted_to_block_schedule
from main import generate_complete_schedule


def test_generate_complete_schedule_constraint_only_minimal_problem_size(
    minimal_case_setup,
):
    # TODO: minimal_case_setup's contents are unnested, don't allow req accumulation
    workers, rotations, weeks, requirements = minimal_case_setup

    overrides = pl.DataFrame()
    requests = pl.DataFrame()

    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides, requests
    )

    assert isinstance(solved_schedule, pl.DataFrame)

    logger.warning("TODO: needs comprehensive validation")

    block_schedule = convert_melted_to_block_schedule(solved_schedule)
    assert isinstance(block_schedule, pl.DataFrame)

    logger.warning("TODO: convert_melted_to_block_schedule is untested. Verify all outputs.")
