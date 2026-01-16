import warnings
from datetime import timedelta
from typing import Union

import box
import cpmpy as cp
import polars as pl
import pytest

import config
from constraints import (
    enforce_minimum_contiguity,
    enforce_requirement_constraints,
    enforce_rotation_capacity_maximum,
    enforce_rotation_capacity_minimum,
    require_one_rotation_per_resident_per_week,
    force_literal_value_over_range,
)
from data_io import generate_pl_wrapped_boolvar
from display import (
    extract_solved_schedule,
    convert_melted_to_block_schedule,
    reconstruct_melted_from_block_schedule,
)
from requirement_builder import RequirementBuilder
from selection import group_scheduled_df_by_for_each, subset_scheduled_by

real_size_residents = pl.read_csv(
    config.TESTING_FILES["residents"]["real_size_seniors"]
)
real_size_rotations = pl.read_csv(config.TESTING_FILES["rotations"]["real_size"])
one_academic_year_weeks = pl.read_csv(
    config.TESTING_FILES["weeks"]["full_academic_year_2025_2026"], try_parse_dates=True
)


def dump_resulting_block(
    melted_solved_schedule: pl.DataFrame, csv_filepath="scratch_output.csv"
) -> None:
    from display import convert_melted_to_block_schedule

    block_schedule = convert_melted_to_block_schedule(melted_solved_schedule)
    block_schedule.write_csv(csv_filepath)


def test_require_one_rotation_per_resident_per_week() -> None:

    rotations = real_size_rotations
    weeks = one_academic_year_weeks

    residents = real_size_residents
    residents = residents.filter(pl.col("year").is_in((["R2", "R3"])))
    warnings.warn("filtering out extended-R3s")

    model = cp.Model()

    test_scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)
    test_constraints = require_one_rotation_per_resident_per_week(
        residents,
        rotations,
        weeks,
        scheduled=test_scheduled,
    )

    model += test_constraints
    is_feasible = model.solve("ortools", log_search_progress=False)
    if not is_feasible:
        raise ValueError("Infeasible")

    solved_schedule = extract_solved_schedule(test_scheduled)

    assert verify_one_rotation_per_resident_per_week(
        solved_schedule,
    ), "verify_one_rotation_per_resident_per_week == False"


def verify_one_rotation_per_resident_per_week(solved_schedule) -> bool:
    """
    Notes:
        This will be invalid if it shouldn't apply over the entire solved range.
    Args:
        solved_schedule: solved schedule♥

    Returns:
        bool: True if passes
    """
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        solved_schedule,
        for_each_individual=["resident", "week"],
        group_on_column=config.CPMPY_RESULT_COLUMN,
    )
    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[config.CPMPY_RESULT_COLUMN]

        assert sum(decision_vars) == 1, f"sum decision_vars = {decision_vars} != 1"

    return True


def test_enforce_rotation_capacity_minimum() -> None:
    residents = real_size_residents
    rotations = real_size_rotations
    weeks = one_academic_year_weeks

    rotations_with_minimum_residents = rotations.filter(
        pl.col("minimum_residents_assigned") > 0
    )

    test_scheduled = generate_pl_wrapped_boolvar(
        residents=residents,
        rotations=rotations_with_minimum_residents,
        weeks=weeks,
    )
    test_constraints = enforce_rotation_capacity_minimum(
        residents=residents,
        rotations=rotations_with_minimum_residents,
        weeks=weeks,
        scheduled=test_scheduled,
    )
    model = cp.Model()
    model += test_constraints
    model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)

    solved_schedule = extract_solved_schedule(test_scheduled)

    assert verify_enforce_rotation_capacity_minimum(
        rotations,
        solved_schedule,
    ), "verify_enforce_rotation_capacity_minimum == False"


def verify_enforce_rotation_capacity_minimum(rotations, solved_schedule) -> bool:
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        solved_schedule,
        for_each_individual=["rotation", "week"],
        group_on_column=config.CPMPY_RESULT_COLUMN,
    )
    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[config.CPMPY_RESULT_COLUMN]
        if decision_vars:
            rotation = rotations.filter(pl.col("rotation") == group_dict["rotation"])
            min_residents_this_rotation = rotation.select(
                pl.col("minimum_residents_assigned")
            ).item()
            if min_residents_this_rotation is None:
                min_residents_this_rotation = 0

            assert (
                sum(decision_vars) >= min_residents_this_rotation
            ), f"sum decision_vars = {decision_vars} != minimum_residents_assigned for {rotation}"
    return True


def test_enforce_rotation_capacity_maximum() -> None:
    residents = real_size_residents
    rotations = real_size_rotations
    weeks = one_academic_year_weeks

    rotations_with_minimum_residents = rotations.filter(
        pl.col("maximum_residents_assigned") > 0
    )

    test_scheduled = generate_pl_wrapped_boolvar(
        residents=residents,
        rotations=rotations_with_minimum_residents,
        weeks=weeks,
    )
    test_constraints = enforce_rotation_capacity_maximum(
        residents=residents,
        rotations=rotations_with_minimum_residents,
        weeks=weeks,
        scheduled=test_scheduled,
    )
    model = cp.Model()
    model += test_constraints
    model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)

    solved_schedule = extract_solved_schedule(test_scheduled)

    assert verify_enforce_rotation_capacity_maximum(
        rotations,
        solved_schedule,
    ), "verify_enforce_rotation_capacity_maximum == False"


def verify_enforce_rotation_capacity_maximum(rotations, solved_schedule) -> bool:
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        solved_schedule,
        for_each_individual=["rotation", "week"],
        group_on_column=config.CPMPY_RESULT_COLUMN,
    )
    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[config.CPMPY_RESULT_COLUMN]
        if decision_vars:
            rotation = rotations.filter(pl.col("rotation") == group_dict["rotation"])
            max_residents_this_rotation = rotation.select(
                pl.col("maximum_residents_assigned")
            ).item()
            if max_residents_this_rotation is None:
                assert (
                    False
                ), f"max_residents_this_rotation == {max_residents_this_rotation}? Doesn't make sense."

            assert (
                sum(decision_vars) <= max_residents_this_rotation
            ), f"sum decision_vars = {decision_vars} != maximum_residents_assigned for {rotation}"
    return True


def test_enforce_minimum_contiguity() -> None:
    """
    Note the source of contiguity is now the requirements pathway (see requirement_builder.py).
    This remains as a proof on concept on the algorithm but is not going to be used in production.
    """
    residents = real_size_residents
    residents = residents.filter(pl.col("year").is_in(["R2", "R3"]))

    rotations = real_size_rotations
    weeks = one_academic_year_weeks

    scheduled = generate_pl_wrapped_boolvar(
        residents=residents,
        rotations=rotations,
        weeks=weeks,
    )

    model = cp.Model()

    rotations_with_minimum_contiguity = rotations.filter(
        (pl.col("minimum_contiguous_weeks") > 1)
        & (pl.col("minimum_contiguous_weeks").is_not_null())
    )
    contiguity_constraints = enforce_minimum_contiguity(
        "use_rotations_data",
        residents,
        rotations_with_minimum_contiguity,
        weeks,
        scheduled,
    )

    model += contiguity_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled=scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)
    assert verify_minimum_contiguity(
        "use_rotations_data",
        residents,
        rotations_with_minimum_contiguity,
        weeks,
        melted_solved_schedule,
    )


def verify_minimum_contiguity(
    constraint: Union[box.Box, str],
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    """
    Verify that the solved schedule respects minimum contiguity constraints.

    Args:
        constraint: python-box describing minimum contiguity constraint or "use_rotations_data" which will pull instead from the rotations dataframe. (This is not the intended final function.)
        residents:
        rotations: DataFrame with rotations that have minimum_contiguous_weeks constraints
        weeks:
        solved_schedule: Melted schedule DataFrame with columns:
                        ['resident', 'rotation', 'week', 'scheduled'] where
                        'scheduled' is boolean indicating if resident is on rotation that week

    Returns:
        bool: True if all contiguity constraints are satisfied, False otherwise
    """
    for rotation_dict in rotations.iter_rows(named=True):

        rotation_name = rotation_dict[config.ROTATIONS_PRIMARY_LABEL]
        if constraint == "use_rotations_data":
            min_contiguity = rotation_dict["minimum_contiguous_weeks"]
        else:
            min_contiguity = constraint.weeks  # type: ignore

        rotation_schedule = solved_schedule.filter(
            (pl.col("rotation") == rotation_name)
            & (pl.col(config.CPMPY_RESULT_COLUMN) == True)  # noqa: E712
        )

        for resident_dict in residents.iter_rows(named=True):
            resident_rotation_schedule = rotation_schedule.filter(
                pl.col("resident") == resident_dict
            ).sort("week")

            scheduled_weeks = resident_rotation_schedule["week"].to_list()
            contiguous_blocks = find_contiguous_blocks(scheduled_weeks)

            for block in contiguous_blocks:
                if len(block) < min_contiguity:
                    print(
                        f"CONTIGUITY VIOLATION: Resident {resident_dict} on rotation {rotation_name}"
                    )
                    print(f"  Has block of length {len(block)}: {block}")
                    print(f"  But minimum contiguity is {min_contiguity}")
                    return False

    return True


def find_contiguous_blocks(week_list: list) -> list[list]:
    """
    Find all contiguous blocks in a list of week numbers/identifiers.

    Args:
        week_list: List of week identifiers (could be dates or week numbers, but in strange degraded state could be strings)

    Returns:
        List of lists, each containing a contiguous block of weeks
    """
    if not week_list:
        return []

    sorted_weeks = sorted(week_list)
    blocks = []
    current_block = [sorted_weeks[0]]

    for i in range(1, len(sorted_weeks)):
        if is_consecutive(sorted_weeks[i - 1], sorted_weeks[i]):
            current_block.append(sorted_weeks[i])
        else:
            # Start a new block
            blocks.append(current_block)
            current_block = [sorted_weeks[i]]

    blocks.append(current_block)

    return blocks


def is_consecutive(week1, week2) -> bool:
    """
    Check if week1 and week2 are consecutive and ordered week1 -> week2.

    Args:
        week1, week2: Week identifiers - should be datetime from weeks dataframe but could be integer week numbers (as judged from academic year start)

    Returns:
        bool: True if week2 immediately follows week1 (== 1 week later)
    """
    # If weeks are date-flavored objects
    if hasattr(week1, "year") and hasattr(week2, "year"):
        return week2 == week1 + timedelta(weeks=1)

    # If weeks are integers representing week numbers
    if isinstance(week1, int) and isinstance(week2, int):
        return week2 == week1 + 1

    # If weeks are strings, try conversion to integers assuming bad conversion (worst possible)
    try:
        return int(week2) == int(week1) + 1
    except (ValueError, TypeError):
        print("failed even to convert to string")

    # Fall back to string comparison (not ideal)
    return str(week2) == str(int(str(week1)) + 1)


@pytest.fixture
def sample_barely_fit_R2s_no_prereqs():
    residents = pl.DataFrame(
        {
            "full_name": ["First Guy", "Second Guy", "Third Guy", "Fourth Guy"],
            "year": ["R2", "R2", "R2", "R2"],
        }
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Green HS Senior", "Orange HS Senior", "Elective"],
            "category": ["HS Rounding Senior", "HS Rounding Senior", "Elective"],
            "required_role": ["Senior", "Senior", "Any"],
            "minimum_residents_assigned": [1, 1, 0],
            "maximum_residents_assigned": [1, 1, 10],
            "minimum_contiguous_weeks": [2, 2, None],
        }
    )
    weeks = one_academic_year_weeks.head(n=8)

    builder = RequirementBuilder()
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=[
                "Green HS Senior",
                "Orange HS Senior",
            ],
        )
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(12, ["R2"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()

    scheduled = generate_pl_wrapped_boolvar(
        residents,
        rotations,
        weeks,
    )
    prior_rotations_completed = pl.DataFrame(
        {
            "resident": [],
            "rotation": [],
            "completed_weeks": [],
        }
    )

    return (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    )


@pytest.fixture
def sample_simple_prerequisites_no_priors() -> (
    tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, box.Box, pl.DataFrame, pl.DataFrame]
):
    residents = pl.DataFrame(
        {
            "full_name": ["First Guy", "Second Guy", "Third Guy"],
            "year": ["R2", "R2", "R2"],
        }
    )
    rotations = pl.DataFrame(
        {
            "rotation": [
                "Green HS Senior",
                "Orange HS Senior",
                "Elective",
                "Purple HS Senior",
            ],
            "category": [
                "HS Rounding Senior",
                "HS Rounding Senior",
                "Elective",
                "HS Admitting Senior",
            ],
            "required_role": ["Senior", "Senior", "Any", "Senior"],
            "minimum_residents_assigned": [0, 0, 0, 1],
            "maximum_residents_assigned": [1, 1, 10, 1],
            "minimum_contiguous_weeks": [2, 2, None, 2],
        }
    )
    weeks = one_academic_year_weeks.head(n=8)

    builder = RequirementBuilder()
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=[
                "Green HS Senior",
                "Orange HS Senior",
            ],
        )
        .min_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
        .after_prerequisite(
            prereq_fulfilling_rotations=["Purple HS Senior"],
            weeks_required=2,  # deliberately short so that the four can rotate through Elective to get out of the way
            resident_years=["R2"],
        )
    )
    (
        builder.add_requirement(
            name="HS Admitting Senior", fulfilled_by=["Purple HS Senior"]
        )
        .min_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(12, ["R2"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()

    scheduled = generate_pl_wrapped_boolvar(
        residents,
        rotations,
        weeks,
    )

    prior_rotations_completed = pl.DataFrame(
        {
            "resident": [],
            "rotation": [],
            "completed_weeks": [],
        }
    )

    return (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    )


def test_enforce_prerequisites_with_no_priors(
    sample_simple_prerequisites_no_priors,
):

    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_simple_prerequisites_no_priors

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"


@pytest.fixture
def sample_simple_prerequisites_with_priors():
    residents = pl.DataFrame(
        {
            "full_name": [
                "Already Did Purple Guy",
                "Never Done Purple Guy",
                "Other Never Purple Guy",
            ],
            "year": ["R2", "R2", "R2"],
        }
    )
    rotations = pl.DataFrame(
        {
            "rotation": [
                "Green HS Senior",
                # "Orange HS Senior",
                "Elective",
                "Purple HS Senior",
            ],
            "category": [
                "HS Rounding Senior",
                # "HS Rounding Senior",
                "Elective",
                "HS Admitting Senior",
            ],
            "required_role": [
                "Senior",
                # "Senior",
                "Any",
                "Senior",
            ],
            "minimum_residents_assigned": [
                1,
                # 1,
                0,
                1,
            ],
            "maximum_residents_assigned": [
                1,
                # 1,
                10,
                1,
            ],
            "minimum_contiguous_weeks": [
                2,
                # 2,
                None,
                2,
            ],
        }
    )
    weeks = one_academic_year_weeks.head(n=4)

    builder = RequirementBuilder()
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=[
                "Green HS Senior",
                # "Orange HS Senior",
            ],
        ).min_weeks_over_resident_years(1, ["R2"])
        # .min_contiguity_over_resident_years(2, ["R2"])
        .after_prerequisite(
            prereq_fulfilling_rotations=["Purple HS Senior"],
            weeks_required=1,  # deliberately short so that the four can rotate through Elective to get out of the way
            resident_years=["R2"],
        )
    )
    (
        builder.add_requirement(
            name="HS Admitting Senior", fulfilled_by=["Purple HS Senior"]
        ).min_weeks_over_resident_years(1, ["R2"])
        # .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(12, ["R2"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()

    scheduled = generate_pl_wrapped_boolvar(
        residents,
        rotations,
        weeks,
    )

    prior_rotations_completed = pl.DataFrame(
        {
            "resident": [
                "Already Did Purple Guy",
            ],
            "rotation": ["Purple HS Senior"],
            "completed_weeks": [2],
        }
    )

    return (
        residents,
        rotations,
        weeks,
        current_requirements,
        scheduled,
        prior_rotations_completed,
    )


def verify_prerequisite_met(
    prereq_weeks: int,
    prereq_demanding_rotations: list[str],
    prereq_fulfilling_rotations: list[str],
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    prior_rotations_completed: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    for resident_dict in residents.iter_rows(named=True):
        resident_name = resident_dict[config.RESIDENTS_PRIMARY_LABEL]
        completed_weeks_prior_years: int = (
            prior_rotations_completed.filter(
                (pl.col("resident") == resident_name)
                & (pl.col("rotation").is_in(prereq_fulfilling_rotations))
            )
            .select("completed_weeks")
            .sum()
            .item()
        )
        if completed_weeks_prior_years is None:
            completed_weeks_prior_years = 0

        is_resident_already_done: bool = completed_weeks_prior_years >= prereq_weeks
        if is_resident_already_done:
            continue

        for week_dict in weeks.iter_rows(named=True):
            this_week = week_dict[config.WEEKS_PRIMARY_LABEL]

            count_prereq_demanders_scheduled_this_week: int = solved_schedule.filter(
                (pl.col("resident") == resident_name)
                & (pl.col("week") == this_week)
                & (pl.col("rotation").is_in(prereq_demanding_rotations))
            )[config.CPMPY_RESULT_COLUMN].sum()

            is_scheduled_this_week = count_prereq_demanders_scheduled_this_week > 0
            if not is_scheduled_this_week:
                continue

            scheduled_weeks_prior: int = solved_schedule.filter(
                (pl.col("resident") == resident_name)
                & (pl.col("week") < this_week)
                & (pl.col("rotation").is_in(prereq_fulfilling_rotations))
            )[config.CPMPY_RESULT_COLUMN].sum()

            if completed_weeks_prior_years + scheduled_weeks_prior < prereq_weeks:
                return False
    return True


def test_simple_prerequisites_with_priors(sample_simple_prerequisites_with_priors):
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        scheduled,
        prior_rotations_completed,
    ) = sample_simple_prerequisites_with_priors

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print("\n")
        print(">>> Minimum Unsatisfiable Core (MUS): ")
        pprint.pprint(mus(model.constraints))
        print("<<<")
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"


def test_enforce_requirement_constraints_R2s_barely_fit(
    sample_barely_fit_R2s_no_prereqs,
):
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"


def verify_enforce_requirement_constraints(
    requirements: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    prior_rotations_completed: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    for requirement_name, requirement_body in requirements.items():
        for constraint in requirement_body.constraints:
            match constraint.type:
                case "min_by_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_minimum_week_constraint(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_minimum_week_requirement == False"

                case "max_by_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_maximum_week_constraint(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_maximum_week_requirement == False"

                case "exact_by_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_exact_week_constraint(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_exact_week_constraint failed"

                case "min_contiguity_in_period":
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_minimum_contiguity(
                        constraint,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        solved_schedule,
                    ), "verify_minimum_contiguity failed"

                case "prerequisite":
                    prereq_demanding_rotations = requirement_body.fulfilled_by
                    prereq_fulfilling_rotations = constraint.prerequisite_fulfillers
                    prereq_weeks = constraint.weeks
                    residents_subject_to_req = residents.filter(
                        pl.col("year").is_in(constraint.resident_years)
                    )
                    rotations_fulfilling_req = rotations.filter(
                        pl.col("rotation").is_in(requirement_body.fulfilled_by)
                    )
                    assert verify_prerequisite_met(
                        prereq_weeks,
                        prereq_demanding_rotations,
                        prereq_fulfilling_rotations,
                        residents_subject_to_req,
                        rotations_fulfilling_req,
                        weeks,
                        prior_rotations_completed,
                        solved_schedule,
                    ), "verify_exact_week_constraint failed"

                case "max_contiguity_in_period":
                    raise NotImplementedError("Unclear if actually needed")
                case _:
                    raise LookupError(
                        f"{constraint.type=} is not a known requirement constraint type"
                    )
    return True


def verify_minimum_week_constraint(
    constraint: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    relevant_schedule = subset_scheduled_by(
        residents, rotations, weeks, solved_schedule
    )
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        subset_scheduled=relevant_schedule,
        for_each_individual="resident",
        group_on_column=config.CPMPY_RESULT_COLUMN,
    )

    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[config.CPMPY_RESULT_COLUMN]

        if sum(decision_vars) < constraint.weeks:
            print(f"{sum(decision_vars)=} < {constraint=} !!!")
            return False
    return True


def verify_maximum_week_constraint(
    constraint: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    relevant_schedule = subset_scheduled_by(
        residents, rotations, weeks, solved_schedule
    )
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        subset_scheduled=relevant_schedule,
        for_each_individual="resident",
        group_on_column=config.CPMPY_RESULT_COLUMN,
    )

    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[config.CPMPY_RESULT_COLUMN]

        if sum(decision_vars) > constraint.weeks:
            print(f"{sum(decision_vars)=} > {constraint=} !!!")
            return False
    return True


def verify_exact_week_constraint(
    constraint: box.Box,
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    solved_schedule: pl.DataFrame,
) -> bool:
    relevant_schedule = subset_scheduled_by(
        residents, rotations, weeks, solved_schedule
    )
    grouped_solved_schedule = group_scheduled_df_by_for_each(
        subset_scheduled=relevant_schedule,
        for_each_individual="resident",
        group_on_column=config.CPMPY_RESULT_COLUMN,
    )

    for group_dict in grouped_solved_schedule.iter_rows(named=True):
        decision_vars = group_dict[config.CPMPY_RESULT_COLUMN]

        if sum(decision_vars) != constraint.weeks:
            print(f"{sum(decision_vars)=} != {constraint=} !!!")
            return False
    return True


@pytest.fixture
def sample_literal_reqs_matching_barely_fit_R2_no_prereqs_single_element(
    sample_barely_fit_R2s_no_prereqs,
):
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    resident_target = ["Fourth Guy"]
    rotation_target = ["Green HS Senior"]
    week_target = weeks.head(1)

    subset_scheduled_for_literal = scheduled.filter(
        (pl.col("resident").is_in(resident_target))
        & (pl.col("rotation").is_in(rotation_target))
        & (pl.col("week").is_in(week_target[config.WEEKS_PRIMARY_LABEL]))
    )

    literal = True

    return subset_scheduled_for_literal, literal


def test_force_literal_value_over_range_single_element(
    sample_barely_fit_R2s_no_prereqs,
    sample_literal_reqs_matching_barely_fit_R2_no_prereqs_single_element,
):
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    scheduled_subset_constrained_to_literal, literal = (
        sample_literal_reqs_matching_barely_fit_R2_no_prereqs_single_element
    )

    model += force_literal_value_over_range(
        scheduled_subset_constrained_to_literal, literal
    )

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"

    melted_solved_schedule_targeted_to_literal = melted_solved_schedule.join(
        scheduled_subset_constrained_to_literal,
        on=["resident", "rotation", "week"],
        how="inner",
    )

    assert verify_literal_value_over_range(
        melted_solved_schedule_targeted_to_literal, literal
    )


@pytest.fixture
def sample_literal_reqs_matching_barely_fit_R2_no_prereqs_block_element(
    sample_barely_fit_R2s_no_prereqs,
):
    """
    Sample subset of scheduled dataframe which requires "Fourth Guy" never to be on Green over the 8 weeks available.
    """
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    resident_target = ["Fourth Guy"]
    rotation_target = ["Green HS Senior"]
    week_target = weeks.head(8)

    subset_scheduled_for_literal = scheduled.filter(
        (pl.col("resident").is_in(resident_target))
        & (pl.col("rotation").is_in(rotation_target))
        & (pl.col("week").is_in(week_target[config.WEEKS_PRIMARY_LABEL].implode()))
    )

    literal = False

    return subset_scheduled_for_literal, literal


def test_force_literal_value_over_range_block_element(
    sample_barely_fit_R2s_no_prereqs,
    sample_literal_reqs_matching_barely_fit_R2_no_prereqs_block_element,
):
    """
    Excludes "Fourth Guy" from Green during all 8 weeks in question.
    """
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    scheduled_subset_constrained_to_literal, literal = (
        sample_literal_reqs_matching_barely_fit_R2_no_prereqs_block_element
    )

    model += force_literal_value_over_range(
        scheduled_subset_constrained_to_literal, literal
    )

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"

    melted_solved_schedule_targeted_to_literal = melted_solved_schedule.join(
        scheduled_subset_constrained_to_literal,
        on=["resident", "rotation", "week"],
        how="inner",
    )

    assert verify_literal_value_over_range(
        melted_solved_schedule_targeted_to_literal, literal
    )


@pytest.fixture
def sample_literal_reqs_matching_barely_fit_R2_no_prereqs_weekwise(
    sample_barely_fit_R2s_no_prereqs,
):
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    subset_scheduled_for_literal = scheduled.filter(
        (pl.col("resident").is_in(["Fourth Guy"]))
        & (pl.col("rotation").is_in(["Green HS Senior"]))
        & (pl.col("week").is_in(weeks.row(1, named=True)[config.WEEKS_PRIMARY_LABEL]))
    )

    literal = False

    return subset_scheduled_for_literal, literal


def test_force_literal_value_over_range_weekwise(
    sample_barely_fit_R2s_no_prereqs,
    sample_literal_reqs_matching_barely_fit_R2_no_prereqs_weekwise,
):
    """
    Args:
        sample_barely_fit_R2s_no_prereqs: fixture with R2s only which barely fit (4 residents having to do 4 weeks of one of two rotations over 8 weeks)
        sample_literal_reqs_matching_barely_fit_R2_no_prereqs_weekwise: demands that first week has a certain composition
    """
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    scheduled_subset_constrained_to_literal, literal = (
        sample_literal_reqs_matching_barely_fit_R2_no_prereqs_weekwise
    )

    model += force_literal_value_over_range(
        scheduled_subset_constrained_to_literal, literal
    )

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    blockmode = convert_melted_to_block_schedule(melted_solved_schedule)

    dump = blockmode.to_init_repr()

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"

    melted_solved_schedule_targeted_to_literal = melted_solved_schedule.join(
        scheduled_subset_constrained_to_literal,
        on=["resident", "rotation", "week"],
        how="inner",
    )

    assert verify_literal_value_over_range(
        melted_solved_schedule_targeted_to_literal, literal
    )


@pytest.fixture
def sample_literal_reqs_matching_barely_fit_R2_no_prereqs_lock_past_weeks(
    sample_barely_fit_R2s_no_prereqs,
):

    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    goal_block = pl.DataFrame(
        [
            pl.Series(
                "resident",
                ["First Guy", "Second Guy", "Third Guy", "Fourth Guy"],
                dtype=pl.String,
            ),
            pl.Series(
                "2025-06-30",
                ["Elective", "Elective", "Orange HS Senior", "Green HS Senior"],
                dtype=pl.String,
            ),
            pl.Series(
                "2025-07-07",
                ["Elective", "Elective", "Orange HS Senior", "Green HS Senior"],
                dtype=pl.String,
            ),
        ]
    )

    melted = reconstruct_melted_from_block_schedule(goal_block).select(
        pl.all().exclude(config.CPMPY_RESULT_COLUMN)
    )

    subset_scheduled_for_literal = scheduled.join(
        melted, how="inner", on=["resident", "rotation", "week"]
    )

    literal = True

    return subset_scheduled_for_literal, literal


def test_force_literal_value_over_range_lock_past_weeks(
    sample_barely_fit_R2s_no_prereqs,
    sample_literal_reqs_matching_barely_fit_R2_no_prereqs_lock_past_weeks,
):
    """
    Args:
        sample_barely_fit_R2s_no_prereqs: fixture with R2s only which barely fit (4 residents having to do 4 weeks of one of two rotations over 8 weeks)
    """
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        prior_rotations_completed,
        scheduled,
    ) = sample_barely_fit_R2s_no_prereqs

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    scheduled_subset_constrained_to_literal, literal = (
        sample_literal_reqs_matching_barely_fit_R2_no_prereqs_lock_past_weeks
    )

    model += force_literal_value_over_range(
        scheduled_subset_constrained_to_literal, literal
    )

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"

    melted_solved_schedule_targeted_to_literal = melted_solved_schedule.join(
        scheduled_subset_constrained_to_literal,
        on=["resident", "rotation", "week"],
        how="inner",
    )

    assert verify_literal_value_over_range(
        melted_solved_schedule_targeted_to_literal, literal
    )


def verify_literal_value_over_range(
    solved_schedule_which_should_equal_literal: pl.DataFrame,
    literal: bool,
) -> bool:
    for scheduled_row_dict in solved_schedule_which_should_equal_literal.iter_rows(
        named=True
    ):
        element_equals_literal = (
            scheduled_row_dict[config.CPMPY_RESULT_COLUMN] == literal
        )
        if not element_equals_literal:
            return False
    return True


@pytest.fixture
def sample_rarely_available_rotation():

    residents = pl.DataFrame(
        {
            "full_name": ["First Guy", "Second Guy", "Third Guy", "Fourth Guy"],
            "year": ["R2", "R2", "R2", "R2"],
        }
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Green HS Senior", "Elective", "SOM"],
            "category": ["HS Rounding Senior", "Elective", "SOM"],
            "required_role": ["Senior", "Any", "Senior"],
            "minimum_residents_assigned": [1, 0, 0],
            "maximum_residents_assigned": [1, 10, 10],
            "minimum_contiguous_weeks": [2, None, 2],
        }
    )
    weeks = one_academic_year_weeks.head(n=16)

    SOM_indices = [1, 7]

    weeks_with_SOM = (
        weeks.with_row_index("index")
        .filter(pl.col("index").is_in(SOM_indices))
        .drop("index")
    )

    builder = RequirementBuilder()
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=[
                "Green HS Senior",
            ],
        )
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(12, ["R2"])
    )
    (
        builder.add_requirement(name="SOM", fulfilled_by=["SOM"])
        .min_weeks_over_resident_years(1, ["R2"])
        .max_weeks_over_resident_years(1, ["R2"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()

    scheduled = generate_pl_wrapped_boolvar(
        residents,
        rotations,
        weeks,
    )

    prior_rotations_completed = pl.DataFrame(
        {
            "resident": [],
            "rotation": [],
            "completed_weeks": [],
        }
    )

    return (
        residents,
        rotations,
        weeks,
        weeks_with_SOM,
        current_requirements,
        scheduled,
        prior_rotations_completed,
    )


def test_rarely_available_rotation(sample_rarely_available_rotation):
    (
        residents,
        rotations,
        weeks,
        weeks_with_SOM,
        current_requirements,
        scheduled,
        prior_rotations_completed,
    ) = sample_rarely_available_rotation

    model = cp.Model()

    requirement_constraints = enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        scheduled,
    )

    model += requirement_constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)

    limited_week_rotation_names = ["SOM"]
    limited_week_rotations = rotations.filter(
        pl.col("rotation").is_in(limited_week_rotation_names)
    )

    excluded_weeks = weeks.join(weeks_with_SOM, on=weeks.columns, how="anti")

    scheduled_subset_subject_to_week_exclusion = subset_scheduled_by(
        residents, limited_week_rotations, excluded_weeks, scheduled
    )
    literal = False

    model += force_literal_value_over_range(
        scheduled_subset_subject_to_week_exclusion, literal
    )

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        from cpmpy.tools import mus
        import pprint

        print()
        pprint.pprint(mus(model.constraints))
        raise ValueError("Infeasible")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    assert verify_enforce_requirement_constraints(
        current_requirements,
        residents,
        rotations,
        weeks,
        prior_rotations_completed,
        melted_solved_schedule,
    ), "verify_enforce_requirement_constraints returns False"

    melted_solved_schedule_for_weeks = extract_solved_schedule(
        scheduled_subset_subject_to_week_exclusion
    )

    assert verify_literal_value_over_range(
        melted_solved_schedule_for_weeks, literal=False
    )


def test_enforce_block_alignment():
    raise NotImplementedError
