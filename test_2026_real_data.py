import warnings

import box
import cpmpy as cp
import polars as pl
import polars.selectors as cs
import pytest

import config
from constraints import (
    enforce_requirement_constraints,
    enforce_rotation_capacity_maximum,
    enforce_rotation_capacity_minimum,
    require_one_rotation_per_resident_per_week,
    get_MUS,
)
from data_io import generate_pl_wrapped_boolvar
from display import (
    extract_solved_schedule,
    convert_melted_to_block_schedule,
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
    R3_primary_care_tract_reqs = generate_R3_primary_care_track_reqs()

    current_requirements = {
        "R2_standard": R2_standard_reqs,
        "R2_PCT": R2_primary_care_track_reqs,
        "R3_standard": R3_standard_reqs,
        "R3_PCT": R3_primary_care_tract_reqs,
    }

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


def generate_R2_base_reqs_builder() -> RequirementBuilder:
    builder = RequirementBuilder()
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=["Green HS Senior", "Orange HS Senior"],
        )
        .min_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
        .max_contiguity_over_resident_years(4, ["R2"])
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
    return builder


def generate_R2_standard_reqs() -> box.Box:
    builder = generate_R2_base_reqs_builder()
    current_requirements = builder.accumulate_constraints_by_rule()
    return current_requirements


def generate_R2_primary_care_track_reqs() -> box.Box:
    builder = generate_R2_base_reqs_builder()
    (
        builder.add_requirement(name="GIM", fulfilled_by=["GIM"])
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )

    current_requirements = builder.accumulate_constraints_by_rule()
    return current_requirements


def generate_R3_base_reqs_builder() -> RequirementBuilder:
    builder = RequirementBuilder()
    # 8wk HS rounding
    (
        builder.add_requirement(
            "HS Rounding Senior",
            fulfilled_by=["Green HS Senior", "Orange HS Senior"],
        )
        .min_weeks_over_resident_years(8, ["R3"])
        .min_contiguity_over_resident_years(4, ["R3"])
    )
    # 1-2 NF
    (
        builder.add_requirement(name="Night Senior", fulfilled_by=["Night Senior"])
        .min_weeks_over_resident_years(1, ["R3"])
        .max_weeks_over_resident_years(2, ["R3"])
    )
    # 4 hosp
    (
        builder.add_requirement(
            name="Hospitalist", fulfilled_by=["Hospitalist"]
        ).min_weeks_over_resident_years(4, ["R3"])
    )
    # 4 IP cards
    (
        builder.add_requirement(
            name="IP Cardiology Senior", fulfilled_by=["IP Cardiology Senior"]
        )
        .min_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(2, ["R3"])
    )
    # 4 OP pulm
    (
        builder.add_requirement(name="OP Pulmonology", fulfilled_by=["OP Pulmonology"])
        .min_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(2, ["R3"])
    )
    # electives
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(20, ["R3"])
    )
    (
        builder.add_requirement(
            name="Vacation", fulfilled_by=["Vacation"]
        ).exact_weeks_over_resident_years(4, ["R3"])
    )
    (
        builder.add_requirement(
            name="OP Cardiology", fulfilled_by=["OP Cardiology"]
        ).exact_weeks_over_resident_years(0, ["R3"])
    )

    return builder


def generate_R3_standard_reqs() -> box.Box:
    builder = generate_R3_base_reqs_builder()
    # 4 amb
    (
        builder.add_requirement(name="STHC Senior", fulfilled_by=["STHC Senior"])
        .min_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(4, ["R3"])
    )
    # 4 ICU or CICU
    (
        builder.add_requirement(
            name="ICU Senior", fulfilled_by=["SHMC ICU Senior", "SHMC CICU"]
        )
        .min_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(4, ["R3"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()
    return current_requirements


def generate_R3_primary_care_track_reqs() -> box.Box:
    builder = generate_R3_base_reqs_builder()
    # 4 amb + 4
    (
        builder.add_requirement(name="STHC Senior", fulfilled_by=["STHC Senior"])
        .min_weeks_over_resident_years(8, ["R3"])
        .min_contiguity_over_resident_years(4, ["R3"])
    )
    # GIM 4 / 2*2wk
    (
        builder.add_requirement(name="GIM", fulfilled_by=["GIM"])
        .min_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(2, ["R3"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()
    return current_requirements


@pytest.mark.skip(reason="for introspection only")
def test_2026_req_generation():
    R2_standard_reqs = generate_R2_standard_reqs()
    R2_primary_care_track_reqs = generate_R2_primary_care_track_reqs()
    R3_standard_reqs = generate_R3_standard_reqs()
    R3_primary_care_tract_reqs = generate_R3_primary_care_track_reqs()
    assert True


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

    residents = residents.filter(pl.col("year") != "super_R3")
    warnings.warn("filtering out super_R3s")

    requirement_constraints = list()

    for label, filtered_resident_group in residents.group_by(pl.col("year", "track")):
        match label:
            case ("R2", "PCT"):
                relevant_requirements = current_requirements["R2_PCT"]
            case ("R3", "PCT"):
                relevant_requirements = current_requirements["R3_PCT"]
            case ("R2", "fellowship") | ("R2", "standard"):
                relevant_requirements = current_requirements["R2_standard"]
            case ("R3", "fellowship") | ("R3", "standard"):
                relevant_requirements = current_requirements["R3_standard"]
            case _:
                raise ValueError("Label not accounted for")

        this_group_requirement_constraints = enforce_requirement_constraints(
            relevant_requirements,
            filtered_resident_group,
            rotations,
            weeks,
            prior_rotations_completed,
            scheduled,
        )

        requirement_constraints.extend(this_group_requirement_constraints)

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

    is_feasible = model.solve()
    if not is_feasible:
        min_unsat_result = get_MUS(model)
        print(min_unsat_result)
        raise ValueError("Infeasible")
    melted_solved_schedule = extract_solved_schedule(scheduled)

    block = convert_melted_to_block_schedule(melted_solved_schedule)

    block.write_excel(
        "test_2026_output.xlsx",
        conditional_formats={
            cs.all(): [
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "Green",
                    "format": {"bg_color": "#88E788"},
                },
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "Orange",
                    "format": {"bg_color": "#FFA500"},
                },
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "Purple",
                    "format": {"bg_color": "#b758e0"},
                },
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "Night",
                    "format": {"bg_color": "#898bfa"},
                },
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "STHC",
                    "format": {"bg_color": "#f57171"},
                },
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "SHMC ICU Senior",
                    "format": {"bg_color": "#77edd3"},
                },
                {
                    "type": "text",
                    "criteria": "containing",
                    "value": "Systems of Medicine",
                    "format": {"bg_color": "#ede977"},
                },
            ]
        },
    )

    for label, filtered_resident_group in residents.group_by(pl.col("year", "track")):
        match label:
            case ("R2", "PCT"):
                relevant_requirements = current_requirements["R2_PCT"]
            case ("R3", "PCT"):
                relevant_requirements = current_requirements["R3_PCT"]
            case ("R2", "fellowship") | ("R2", "standard"):
                relevant_requirements = current_requirements["R2_standard"]
            case ("R3", "fellowship") | ("R3", "standard"):
                relevant_requirements = current_requirements["R3_standard"]
            case _:
                raise ValueError("Label not accounted for")

        assert verify_enforce_requirement_constraints(
            relevant_requirements,
            filtered_resident_group,
            rotations,
            weeks,
            prior_rotations_completed,
            melted_solved_schedule,
        ), "verify_enforce_requirement_constraints returns False"


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
