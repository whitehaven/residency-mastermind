import datetime
import sys
import warnings

import box
import cpmpy as cp
import polars as pl
import polars.selectors as cs
import pytest
from loguru import logger

import config
from constraints import (
    enforce_requirement_constraints,
    enforce_rotation_capacity_maximum,
    enforce_rotation_capacity_minimum,
    require_one_rotation_per_resident_per_week,
    get_MUS,
    force_literal_value_over_range,
)
from data_io import generate_pl_wrapped_boolvar
from display import (
    extract_solved_schedule,
    convert_melted_to_block_schedule,
)
from optimization import (
    generate_blank_preferences_df,
    create_preferences_objective,
    calculate_total_preference_satisfaction,
)
from requirement_builder import RequirementBuilder
from test_constraints import verify_enforce_requirement_constraints

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)

WRITE_2026_XLSX_OUTPUT = True
WRITE_2026_CSV_OUTPUT = False
PERFORM_VERIFICATION = False


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
        .max_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
        .max_contiguity_over_resident_years(4, ["R2"])
        .after_prerequisite(
            prereq_fulfilling_rotations=["HS Admitting Senior"],
            weeks_required=2,
            resident_years=["R2"],
        )
        .must_respect_block_alignment(["R2"])
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
        .max_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(name="ICU Senior", fulfilled_by=["SHMC ICU Senior"])
        .min_weeks_over_resident_years(4, ["R2"])
        .max_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(
            name="Consults", fulfilled_by=["Consults"]
        ).min_weeks_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(
            name="Hospitalist", fulfilled_by=["Hospitalist"]
        ).exact_weeks_over_resident_years(0, ["R2"])
    )
    (
        builder.add_requirement(name="STHC Senior", fulfilled_by=["STHC Senior"])
        .exact_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
        .max_contiguity_over_resident_years(4, ["R2"])
        .must_respect_block_alignment(["R2"])
    )
    (
        builder.add_requirement(name="OP Cardiology", fulfilled_by=["OP Cardiology"])
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(name="Dermatology", fulfilled_by=["Dermatology"])
        .exact_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(name="Geriatrics", fulfilled_by=["Geriatrics"])
        .exact_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )
    (
        builder.add_requirement(name="Psych Consult", fulfilled_by=["Psych Consult"])
        .exact_weeks_over_resident_years(2, ["R2"])
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
        builder.add_requirement(name="Vacation", fulfilled_by=["Vacation"])
        .exact_weeks_over_resident_years(4, ["R2"])
        .max_contiguity_over_resident_years(1, ["R2"])
    )
    (
        builder.add_requirement(
            name="OP Pulmonology", fulfilled_by=["OP Pulmonology"]
        ).exact_weeks_over_resident_years(0, ["R2"])
    )
    return builder


def generate_R2_standard_reqs() -> box.Box:
    builder = generate_R2_base_reqs_builder()

    # 0 GIM for standard R2
    builder.add_requirement(
        name="GIM", fulfilled_by=["GIM"]
    ).max_weeks_over_resident_years(0, ["R2"])

    current_requirements = builder.accumulate_constraints_by_rule()
    return current_requirements


def generate_R2_primary_care_track_reqs() -> box.Box:
    builder = generate_R2_base_reqs_builder()
    (
        builder.add_requirement(name="GIM", fulfilled_by=["GIM"])
        .exact_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
        .max_contiguity_over_resident_years(2, ["R2"])
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
        .max_contiguity_over_resident_years(4, ["R3"])
        .must_respect_block_alignment(["R3"])
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
        .exact_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(2, ["R3"])
    )
    # electives
    (
        builder.add_requirement(
            name="Elective", fulfilled_by=["Elective"]
        ).max_weeks_over_resident_years(20, ["R3"])
    )
    (
        builder.add_requirement(name="Vacation", fulfilled_by=["Vacation"])
        .exact_weeks_over_resident_years(4, ["R3"])
        .max_contiguity_over_resident_years(1, ["R3"])
    )
    (
        builder.add_requirement(
            name="OP Cardiology", fulfilled_by=["OP Cardiology"]
        ).exact_weeks_over_resident_years(0, ["R3"])
    )
    (
        builder.add_requirement(
            name="Systems of Medicine", fulfilled_by=["Systems of Medicine"]
        ).max_weeks_over_resident_years(0, ["R3"])
    )

    return builder


def generate_R3_standard_reqs() -> box.Box:
    builder = generate_R3_base_reqs_builder()
    # 4 amb
    (
        builder.add_requirement(name="STHC Senior", fulfilled_by=["STHC Senior"])
        .exact_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(4, ["R3"])
        .max_contiguity_over_resident_years(4, ["R3"])
        .must_respect_block_alignment(["R3"])
    )
    # 4 ICU or CICU
    (
        builder.add_requirement(
            name="ICU Senior", fulfilled_by=["SHMC ICU Senior", "SHMC CICU"]
        )
        .exact_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(4, ["R3"])
        .must_respect_block_alignment(["R3"])
    )
    current_requirements = builder.accumulate_constraints_by_rule()
    return current_requirements


def generate_R3_primary_care_track_reqs() -> box.Box:
    builder = generate_R3_base_reqs_builder()
    # 4 amb + 4
    (
        builder.add_requirement(name="STHC Senior", fulfilled_by=["STHC Senior"])
        .min_weeks_over_resident_years(8, ["R3"])
        .min_contiguity_over_resident_years(2, ["R3"])
        .max_contiguity_over_resident_years(4, ["R3"])
    )
    # GIM 4 / 2*2wk
    (
        builder.add_requirement(name="GIM", fulfilled_by=["GIM"])
        .min_weeks_over_resident_years(4, ["R3"])
        .max_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(2, ["R3"])
    )
    (
        builder.add_requirement(
            name="ICU Senior", fulfilled_by=["SHMC ICU Senior", "SHMC CICU"]
        ).exact_weeks_over_resident_years(0, ["R3"])
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


@pytest.mark.skip(reason="Replaced by total solution, test_2026_real_data")
def test_2026_real_data_constraint_only(real_2026_data):
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
    logger.warning("super_R3 filtered out")

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
        logger.success(
            f"created and logged requirements {len(this_group_requirement_constraints)} constraints for {label}, total {len(requirement_constraints)}"
        )
    model += requirement_constraints
    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)
    logger.success(f"Added basic constraints to model")

    logger.debug(f"Generating manual specification constraints...")

    # restrict SOM
    SOM_openings = [
        datetime.date(2026, 10, 12),
        datetime.date(2026, 10, 19),
        datetime.date(2027, 3, 1),
        datetime.date(2027, 3, 8),
    ]
    SOM_unavail = scheduled.filter(
        (~pl.col("week").is_in(SOM_openings))
        & (pl.col("rotation").eq("Systems of Medicine"))
    )
    SOM_constraints = force_literal_value_over_range(SOM_unavail, False)
    model += SOM_constraints
    logger.debug(f"Added {len(SOM_constraints)=}")

    manual_true_targets = pl.read_csv(
        "real_2026_manual_true_constraints.csv", try_parse_dates=True
    )

    manual_true_targets_with_boolvars = scheduled.join(
        manual_true_targets, on=["resident", "rotation", "week"], how="right"
    )

    vacation_constraints = force_literal_value_over_range(
        manual_true_targets_with_boolvars, True
    )
    model += vacation_constraints
    logger.debug(f"Added {len(vacation_constraints)=}")

    total_manual_constraints = len(SOM_constraints) + len(vacation_constraints)

    logger.success(f"Generated {total_manual_constraints=}")

    logger.info(f">> Starting solve...")
    is_feasible = model.solve(
        solver=config.DEFAULT_CPMPY_SOLVER, log_search_progress=True
    )

    if not is_feasible:
        min_unsat_result = get_MUS(model)
        print(min_unsat_result)
        raise ValueError("Infeasible")

    logger.success(f"solver completed; is_feasible = {is_feasible}")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    if PERFORM_VERIFICATION:
        logger.debug(f"Starting constraint verification...")

        for label, filtered_resident_group in residents.group_by(
            pl.col("year", "track")
        ):
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
            logger.debug(f"Starting verification for class {label}")
            assert verify_enforce_requirement_constraints(
                relevant_requirements,
                filtered_resident_group,
                rotations,
                weeks,
                prior_rotations_completed,
                melted_solved_schedule,
            ), "verify_enforce_requirement_constraints returns False"
            logger.success(f"Constraints verified as met for class {label}")
        logger.success(f"All constraints verified successfully.")
    else:
        logger.warning(f"Skipping constraint verification.")

    if WRITE_2026_XLSX_OUTPUT:
        block = convert_melted_to_block_schedule(melted_solved_schedule)
        block = block.join(
            residents, left_on="resident", right_on=config.RESIDENTS_PRIMARY_LABEL
        ).select(
            [
                "resident",
                "year",
                "track",
                cs.all().exclude(["resident", "year", "track"]),
            ]
        )
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
                    {
                        "type": "text",
                        "criteria": "containing",
                        "value": "Vacation",
                        "format": {"bg_color": "#f593d1"},
                    },
                ]
            },
        )
        logger.success("wrote xlsx to test_2026_output.xlsx")
    if WRITE_2026_CSV_OUTPUT:
        block = convert_melted_to_block_schedule(melted_solved_schedule)
        block.write_csv("test_2026_data.csv")
        logger.success("wrote csv to test_2026_data.csv")
    logger.success(">> End of Program <<")


def test_2026_real_data_total(real_2026_data, generate_2026_preferences_dataframe):
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
    logger.warning("super_R3 filtered out")

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
        logger.success(
            f"created and logged requirements {len(this_group_requirement_constraints)} constraints for {label}, total {len(requirement_constraints)}"
        )
    model += requirement_constraints
    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)
    logger.success(f"Added basic constraints to model")

    logger.debug(f"Generating manual specification constraints...")

    # restrict SOM
    SOM_openings = [
        datetime.date(2026, 10, 12),
        datetime.date(2026, 10, 19),
        datetime.date(2027, 3, 1),
        datetime.date(2027, 3, 8),
    ]
    SOM_unavail = scheduled.filter(
        (~pl.col("week").is_in(SOM_openings))
        & (pl.col("rotation").eq("Systems of Medicine"))
    )
    SOM_constraints = force_literal_value_over_range(SOM_unavail, False)
    model += SOM_constraints
    logger.debug(f"Added {len(SOM_constraints)=}")

    manual_true_targets = pl.read_csv(
        "real_2026_manual_true_constraints.csv", try_parse_dates=True
    )

    manual_true_targets_with_boolvars = scheduled.join(
        manual_true_targets, on=["resident", "rotation", "week"], how="right"
    )

    vacation_constraints = force_literal_value_over_range(
        manual_true_targets_with_boolvars, True
    )
    model += vacation_constraints
    logger.debug(f"Added {len(vacation_constraints)=}.")

    total_manual_constraints = len(SOM_constraints) + len(vacation_constraints)

    logger.success(f"Generated {total_manual_constraints=}.")

    logger.info(">> Starting preference assignment...")
    preferences = generate_2026_preferences_dataframe
    preference_maximization = create_preferences_objective(scheduled, preferences)
    model.objective(preference_maximization, minimize=False)
    logger.success(f"Maximization objective compiled and integrated to model.")

    logger.info(f">> Starting solve...")
    is_feasible = model.solve(
        solver=config.DEFAULT_CPMPY_SOLVER, log_search_progress=True, time_limit=60 * 1
    )

    if not is_feasible:
        min_unsat_result = get_MUS(model)
        print(min_unsat_result)
        raise ValueError("Infeasible")

    logger.success(f"solver completed; is_feasible = {is_feasible}")

    melted_solved_schedule = extract_solved_schedule(scheduled)

    logger.info(
        f"Total preference satisfaction = {calculate_total_preference_satisfaction(melted_solved_schedule,preferences)}"
    )

    if PERFORM_VERIFICATION:
        logger.debug(f"Starting constraint verification...")

        for label, filtered_resident_group in residents.group_by(
            pl.col("year", "track")
        ):
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
            logger.debug(f"Starting verification for class {label}")
            assert verify_enforce_requirement_constraints(
                relevant_requirements,
                filtered_resident_group,
                rotations,
                weeks,
                prior_rotations_completed,
                melted_solved_schedule,
            ), "verify_enforce_requirement_constraints returns False"
            logger.success(f"Constraints verified as met for class {label}")
        logger.success(f"All constraints verified successfully.")
    else:
        logger.warning(f"Skipping constraint verification.")

    if WRITE_2026_XLSX_OUTPUT:
        block = convert_melted_to_block_schedule(melted_solved_schedule)
        block = block.join(
            residents, left_on="resident", right_on=config.RESIDENTS_PRIMARY_LABEL
        ).select(
            [
                "resident",
                "year",
                "track",
                cs.all().exclude(["resident", "year", "track"]),
            ]
        )
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
                    {
                        "type": "text",
                        "criteria": "containing",
                        "value": "Vacation",
                        "format": {"bg_color": "#f593d1"},
                    },
                ]
            },
        )
        logger.success("wrote xlsx to test_2026_output.xlsx")
    if WRITE_2026_CSV_OUTPUT:
        block = convert_melted_to_block_schedule(melted_solved_schedule)
        block.write_csv("test_2026_data.csv")
        logger.success("wrote csv to test_2026_data.csv")
    logger.success(">> End of Program <<")


def test_2026_preferences_accumulation(
    generate_2026_preferences_dataframe, real_2026_data
) -> None:
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        scheduled,
        prior_rotations_completed,
    ) = real_2026_data

    preferences = generate_2026_preferences_dataframe

    create_preferences_objective(scheduled, preferences)
    assert True


@pytest.fixture
def generate_2026_preferences_dataframe(real_2026_data) -> pl.DataFrame:
    """

    Returns:

    """
    (
        residents,
        rotations,
        weeks,
        current_requirements,
        scheduled,
        prior_rotations_completed,
    ) = real_2026_data

    preferences = generate_blank_preferences_df(
        residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
        rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
        weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
    )

    # general
    logger.debug("Generating categorical preference values:")

    preferences = preferences.with_columns(
        preference=pl.when((pl.col("rotation") == "Elective"))
        .then(pl.col("preference") + 1)
        .otherwise(pl.col("preference"))
    )

    # specifics
    vacation_preferences = pl.read_csv("real_2026_vacations.csv", try_parse_dates=True)

    # Add vacation preferences
    vacation_preferences = pl.read_csv("real_2026_vacations.csv", try_parse_dates=True)

    for vacation_row in vacation_preferences.iter_rows():
        resident, rotation, week = vacation_row
        preferences = preferences.with_columns(
            preference=pl.when(
                (pl.col("resident") == resident)
                & (pl.col("rotation") == rotation)
                & (pl.col("week") == week)
            )
            .then(pl.col("preference") + config.PAYOUTS["Vacation"])
            .otherwise(pl.col("preference"))
        )

    return preferences
