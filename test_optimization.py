import polars as pl
from loguru import logger

from data_io import compose_requirements_to_workers, convert_melted_to_block_schedule
from main import generate_complete_schedule
from optimization import calculate_total_preference_satisfaction
from test_constraints import (
    starmap_verify_req_constraints,
    starmap_verify_rot_constraints,
    verify_overrides,
)


def test_minimal_preferences_case(minimal_with_preferences_case):
    workers, rotations, weeks, requirements, overrides, preferences = (
        minimal_with_preferences_case
    )

    workers_with_reqs = compose_requirements_to_workers(workers, requirements)

    solved_schedule = generate_complete_schedule(
        workers,
        rotations,
        weeks,
        requirements,
        overrides,
        preferences,
    )

    block = convert_melted_to_block_schedule(solved_schedule)

    with pl.Config(tbl_cols=-1, tbl_width_chars=-1):
        logger.trace(f"Testing minimal case with preferences: {preferences}.")
        logger.trace(block)
        maximized_utility = calculate_total_preference_satisfaction(
            solved_schedule, preferences
        )
        logger.success(f"Optimization function achieved maximum of {maximized_utility}")

    assert starmap_verify_req_constraints(workers_with_reqs, weeks, solved_schedule)
    assert starmap_verify_rot_constraints(rotations, solved_schedule)
    if overrides:
        assert verify_overrides(solved_schedule, overrides)
    logger.success("test_minimal_preferences_case passes")
