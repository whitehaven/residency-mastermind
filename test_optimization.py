import polars as pl
from loguru import logger

from data_io import compose_requirements_to_workers, convert_melted_to_block_schedule
from main import generate_complete_schedule
from test_constraints import (
    starmap_verify_req_constraints,
    starmap_verify_rot_constraints,
    verify_overrides,
)


def test_minimal_preferences_case(minimal_preferences_case):
    workers, rotations, weeks, requirements, overrides = minimal_preferences_case

    workers_with_reqs = compose_requirements_to_workers(workers, requirements)

    solved_schedule = generate_complete_schedule(
        workers, rotations, weeks, requirements, overrides=overrides, requests=None
    )

    block = convert_melted_to_block_schedule(solved_schedule)

    with pl.Config(tbl_cols=-1):
        logger.trace(f"Testing overrides: {overrides}.")
        logger.trace(block)

    assert starmap_verify_req_constraints(workers_with_reqs, weeks, solved_schedule)
    assert starmap_verify_rot_constraints(rotations, solved_schedule)
    assert verify_overrides(solved_schedule, overrides)


# def test_solve_with_optimization(simple_optimization_setup_with_preferences):
#     """Test solving model with optimization objective."""
#     residents, rotations, weeks, scheduled, preferences = (
#         simple_optimization_setup_with_preferences
#     )
#
#     model = cp.Model()
#
#     # Add basic constraints
#     model += require_one_rotation_per_resident_per_week(
#         residents, rotations, weeks, scheduled
#     )
#     model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)
#     model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
#
#     # Create and add objective
#     objective = create_preferences_objective(scheduled, preferences)
#     model.maximize(objective)
#
#     # Solve
#     is_optimal = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
#
#     assert is_optimal, "Model should find optimal solution"
#
#     # Extract and check results
#     solved_schedule = extract_solved_schedule(scheduled)
#     total_satisfaction = calculate_total_preference_satisfaction(
#         solved_schedule, preferences
#     )
