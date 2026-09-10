import sys

import polars as pl
from loguru import logger

from data_io import convert_melted_to_block_schedule
from main import generate_complete_schedule

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)


def test_generate_complete_schedule_constraint_only_minimal_problem_size(
    minimal_case_setup, minimal_req_composition
):
    # TODO: minimal_case_setup's contents are unnested, don't allow req accumulation
    workers, rotations, weeks, _requirements = minimal_case_setup

    requirements = minimal_req_composition

    overrides = pl.DataFrame()
    requests = pl.DataFrame()

    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides, requests
    )

    block_schedule = convert_melted_to_block_schedule(solved_schedule)

    print(block_schedule)
