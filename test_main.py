import polars as pl
from loguru import logger

from data_io import compose_requirements_to_workers, convert_melted_to_block_schedule
from main import generate_complete_schedule
from test_constraints import (
    starmap_verify_req_constraints,
    starmap_verify_rot_constraints,
)


def test_real_data_2025_case_constraints_only(real_2025_case_constraints_only):
    workers, rotations, weeks, requirements = real_2025_case_constraints_only

    workers_with_reqs = compose_requirements_to_workers(workers, requirements)

    with pl.Config(tbl_cols=-1, tbl_width_chars=-1):
        logger.trace(f"{workers_with_reqs=}")

    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides=None, preferences=None
    )
    block = convert_melted_to_block_schedule(solved_schedule)

    with pl.Config(tbl_cols=-1, tbl_width_chars=-1):
        logger.trace(
            "Full test run based on real inputs from 2025 (with names changed)"
        )
        logger.trace(block)

    assert starmap_verify_req_constraints(workers_with_reqs, weeks, solved_schedule)
    assert starmap_verify_rot_constraints(rotations, solved_schedule)
