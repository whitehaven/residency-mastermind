import cpmpy as cp
import polars as pl
import pytest
import box

import config
from constraints import (
    enforce_requirement_constraints,
    enforce_rotation_capacity_maximum,
    enforce_rotation_capacity_minimum,
    require_one_rotation_per_resident_per_week,
)
from data_io import generate_pl_wrapped_boolvar
from display import (
    extract_solved_schedule,
    dump_resulting_block,
)
from requirement_builder import RequirementBuilder
from test_constraints import verify_enforce_requirement_constraints


@pytest.fixture
def real_2026_data():

    residents = pl.read_csv("real_2026_data_residents.csv")
    weeks = pl.read_csv("real_2026_data_weeks.csv", try_parse_dates=True)
    rotations = pl.read_csv("real_2026_data_rotations.csv")

    R2_standard_reqs = generate_R2_standard_reqs()
    R2_primary_care_track_reqs = generate_R2_primary_care_track_reqs()
    R3_standard_reqs = generate_R3_standard_reqs()
    R3_primary_care_tract_reqs = generate_R3_primary_care_tract_reqs()

    current_requirements = (
        R2_standard_reqs,
        R2_primary_care_track_reqs,
        R3_standard_reqs,
        R3_primary_care_tract_reqs,
    )

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
        scheduled,
        prior_rotations_completed,
    )


def generate_R2_standard_reqs() -> box.Box:
    builder = RequirementBuilder()
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=["Green HS Senior", "Orange HS Senior"],
        )
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
        .after_prerequisite(
            prereq_fulfilling_rotations=["HS Admitting Senior"],
            weeks_required=2,
            resident_years=["R2"],
        )
    )
    (
        builder.add_requirement(
            name="HS Admitting Senior", fulfilled_by=["Purple HS Senior"]
        )
        .min_weeks_over_resident_years(5, ["R2"])
        .max_weeks_over_resident_years(6, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(name="Night Senior", fulfilled_by=["Night Senior"])
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
    )

    (
        builder.add_requirement(name="ICU Senior", fulfilled_by=["SHMC ICU Senior"])
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
    )

    (
        builder.add_requirement(
            name="Consults", fulfilled_by=["Consults"]
        ).min_weeks_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(name="STHC Senior", fulfilled_by=["STHC Senior"])
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(name="OP Cardiology", fulfilled_by=["OP Cardiology"])
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(
            name="Dermatology", fulfilled_by=["Dermatology"]
        ).min_weeks_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(name="Geriatrics", fulfilled_by=["Geriatrics"])
        .min_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(name="Psych Consult", fulfilled_by=["Psych Consult"])
        .min_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(
            name="Systems of Medicine", fulfilled_by=["Systems of Medicine"]
        )
        .exact_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(20, ["R2"])
    )
    (
        builder.add_requirement(
            name="Vacation", fulfilled_by=["Vacation"]
        ).exact_weeks_over_resident_years(4, ["R2"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()
    return current_requirements


def generate_R2_primary_care_track_reqs() -> box.Box:
    pass


def generate_R3_standard_reqs() -> box.Box:
    pass


def generate_R3_primary_care_tract_reqs() -> box.Box:
    pass


def test_2026_real_data_run(real_2026_data):
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        scheduled,
        prior_rotations_completed,
    ) = real_2026_data

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

    # # TODO:  make sure to force literals
    # limited_week_rotation_names = ["SOM"]
    # limited_week_rotations = rotations.filter(
    #     pl.col("rotation").is_in(limited_week_rotation_names)
    # )
    # excluded_weeks = weeks.join(weeks_with_SOM, on=weeks.columns, how="anti")
    #
    # scheduled_subset_subject_to_week_exclusion = subset_scheduled_by(
    #     residents, limited_week_rotations, excluded_weeks, scheduled
    # )
    # literal = False
    #
    # model += force_literal_value_over_range(
    #     scheduled_subset_subject_to_week_exclusion, literal
    # )

    is_feasible = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    if not is_feasible:
        import pprint

        from cpmpy.tools import mus

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

    dump_resulting_block(melted_solved_schedule)


# # TODO:  make sure to force literals

#     melted_solved_schedule_for_weeks = extract_solved_schedule(
#         scheduled_subset_subject_to_week_exclusion
#     )

#     assert verify_literal_value_over_range(
#         melted_solved_schedule_for_weeks, literal=False
#     )
#     melted_solved_schedule_for_weeks = extract_solved_schedule(
#         scheduled_subset_subject_to_week_exclusion
#     )

#     assert verify_literal_value_over_range(
#         melted_solved_schedule_for_weeks, literal=False
#     )
#     )
#     )
