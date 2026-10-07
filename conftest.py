import datetime

import polars as pl
import pytest

# MAYBE may be better to construct dataset in the test rather than precompose it


@pytest.fixture(scope="session")
def small_req_composition() -> dict[str, dict]:
    """Small realistic requirement set for quick composition testing."""
    req_set = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {"min_weeks": 0, "max_weeks": 4},
                "fulfilled_by": [
                    "Green HS Senior",
                    "Orange HS Senior",
                ],
            },
        },
        "R2 PCT": {
            "ICU Senior": {
                "constraints": {"min_weeks": 0, "max_weeks": 4},
                "fulfilled_by": ["SHMC ICU Senior"],
            }
        },
        "R2 Standard": {
            "ICU Senior": {
                "constraints": {"min_weeks": 4, "max_weeks": 4},
                "fulfilled_by": ["SHMC ICU Senior"],
            }
        },
    }

    return req_set


@pytest.fixture(scope="session")
def minimal_req_composition():
    """Minimal requirement set for total solver testing."""
    req_set = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {"min_weeks": 2, "max_weeks": 4},
                "fulfilled_by": [
                    "Green HS Senior",
                    "Orange HS Senior",
                ],
            },
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }

    return req_set


@pytest.fixture(scope="session")
def minimal_case_setup():
    """Minimum realistic input set for quick testing. Includes pre-composed requirement set."""
    workers = pl.DataFrame(
        [
            {"name": "Aaron Aaronson", "year": "R2", "track": "Standard"},
            {"name": "Bill Byornsen", "year": "R2", "track": "PCT"},
        ]
    )
    rotations = {
        "Green HS Senior": {
            "min_workers_assigned": 1,
            "max_workers_assigned": 1,
        },
        "Orange HS Senior": {
            "min_workers_assigned": 1,
            "max_workers_assigned": 1,
        },
        "Vacation": {"max_workers_assigned": 6},
    }
    weeks = pl.DataFrame(
        [
            {"monday_date": "2026-07-06", "week": 1, "block": 1},
            {"monday_date": "2026-07-13", "week": 2, "block": 1},
            {"monday_date": "2026-07-20", "week": 3, "block": 1},
            {"monday_date": "2026-07-27", "week": 4, "block": 1},
        ]
    ).with_columns(pl.col("monday_date").str.to_date())

    requirements = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {"min_weeks": 2, "max_weeks": 4},
                "fulfilled_by": [
                    "Green HS Senior",
                    "Orange HS Senior",
                ],
            },
            "Vacation": {"constraints": {"max_weeks": 4}, "fulfilled_by": ["Vacation"]},
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }

    return workers, rotations, weeks, requirements


@pytest.fixture(scope="session")
def td_workers_three_simple():
    workers = pl.DataFrame(
        [
            {"name": "Aaron Aaronson", "year": "R2", "track": "Standard"},
            {"name": "Bill Byornsen", "year": "R2", "track": "PCT"},
            {"name": "Charles Chrysler", "year": "R2", "track": "PCT"},
        ]
    )
    return workers


@pytest.fixture(scope="session")
def td_workers_four_simple():
    workers = pl.DataFrame(
        [
            {"name": "Aaron Aaronson", "year": "R2", "track": "Standard"},
            {"name": "Bill Byornsen", "year": "R2", "track": "Standard"},
            {"name": "Charles Chrysler", "year": "R2", "track": "Standard"},
            {"name": "Daniel Darrington", "year": "R2", "track": "Standard"},
        ]
    )
    return workers


@pytest.fixture(scope="session")
def td_weeks_six_consecutive():
    weeks = pl.DataFrame(
        [
            {"monday_date": "2026-07-06", "week": 1, "block": 1},
            {"monday_date": "2026-07-13", "week": 2, "block": 1},
            {"monday_date": "2026-07-20", "week": 3, "block": 1},
            {"monday_date": "2026-07-27", "week": 4, "block": 1},
            {"monday_date": "2026-08-04", "week": 5, "block": 2},
            {"monday_date": "2026-08-11", "week": 6, "block": 2},
        ]
    ).with_columns(pl.col("monday_date").str.to_date())
    return weeks


@pytest.fixture(scope="session")
def td_weeks_eight_consecutive():
    weeks = pl.DataFrame(
        [
            {"monday_date": "2026-07-06", "week": 1, "block": 1},
            {"monday_date": "2026-07-13", "week": 2, "block": 1},
            {"monday_date": "2026-07-20", "week": 3, "block": 1},
            {"monday_date": "2026-07-27", "week": 4, "block": 1},
            {"monday_date": "2026-08-04", "week": 5, "block": 2},
            {"monday_date": "2026-08-11", "week": 6, "block": 2},
            {"monday_date": "2026-08-18", "week": 7, "block": 2},
            {"monday_date": "2026-08-25", "week": 8, "block": 2},
        ]
    ).with_columns(pl.col("monday_date").str.to_date())
    return weeks


@pytest.fixture(scope="session")
def td_reqs_minimal_with_min_contiguity():
    requirements = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {"min_weeks": 2, "max_weeks": 4, "min_contiguity": 2},
                "fulfilled_by": [
                    "Green HS Senior",
                    "Orange HS Senior",
                ],
            },
            "Vacation": {"constraints": {"max_weeks": 3}, "fulfilled_by": ["Vacation"]},
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }
    return requirements


@pytest.fixture(scope="session")
def td_reqs_minimal_with_max_contiguity():
    requirements = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {"min_weeks": 2, "max_weeks": 4, "max_contiguity": 2},
                "fulfilled_by": [
                    "Green HS Senior",
                    "Orange HS Senior",
                ],
            },
            "Vacation": {"constraints": {"max_weeks": 3}, "fulfilled_by": ["Vacation"]},
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }
    return requirements


@pytest.fixture(scope="session")
def td_rotations_hs_vacation():
    rotations = {
        "Green HS Senior": {
            "min_workers_assigned": 1,
            "max_workers_assigned": 1,
        },
        "Orange HS Senior": {
            "min_workers_assigned": 1,
            "max_workers_assigned": 1,
        },
        "Vacation": {"max_workers_assigned": 6},
    }
    return rotations


@pytest.fixture(scope="session")
def minimal_min_contiguity_case(
    td_workers_three_simple: pl.DataFrame,
    td_weeks_six_consecutive: pl.DataFrame,
    td_rotations_hs_vacation: dict[str, dict],
    td_reqs_minimal_with_min_contiguity: dict[str, dict],
):
    workers = td_workers_three_simple
    weeks = td_weeks_six_consecutive
    requirements = td_reqs_minimal_with_min_contiguity
    rotations = td_rotations_hs_vacation

    return workers, rotations, weeks, requirements


@pytest.fixture(scope="session")
def minimal_max_contiguity_case(
    td_workers_three_simple: pl.DataFrame,
    td_weeks_six_consecutive: pl.DataFrame,
    td_rotations_hs_vacation: dict[str, dict],
    td_reqs_minimal_with_max_contiguity: dict[str, dict],
):
    workers = td_workers_three_simple
    weeks = td_weeks_six_consecutive
    requirements = td_reqs_minimal_with_max_contiguity
    rotations = td_rotations_hs_vacation

    return workers, rotations, weeks, requirements


@pytest.fixture(scope="session")
def td_rotations_gn_prp_vacation():
    rotations = {
        "Green HS Senior": {
            "min_workers_assigned": 0,
            "max_workers_assigned": 2,
        },
        "Purple HS Senior": {"min_workers_assigned": 0, "max_workers_assigned": 2},
        "Vacation": {"max_workers_assigned": 6},
    }
    return rotations


@pytest.fixture(scope="session")
def td_reqs_minimal_with_prereqs():
    requirements = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 4,
                    "prerequisite": {
                        "weeks": 2,
                        "rots_meeting_prereqs": ["Purple HS Senior"],
                    },
                },
                "fulfilled_by": [
                    "Green HS Senior",
                ],
            },
            "HS Admitting Senior": {
                "constraints": {"min_weeks": 2, "max_weeks": 2},
                "fulfilled_by": ["Purple HS Senior"],
            },
            "Vacation": {"constraints": {"max_weeks": 2}, "fulfilled_by": ["Vacation"]},
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }
    return requirements


@pytest.fixture(scope="session")
def minimal_prerequisites_case(
    td_workers_three_simple: pl.DataFrame,
    td_weeks_six_consecutive: pl.DataFrame,
    td_rotations_gn_prp_vacation: dict[str, dict],
    td_reqs_minimal_with_prereqs: dict[str, dict],
):
    workers = td_workers_three_simple
    rotations = td_rotations_gn_prp_vacation
    weeks = td_weeks_six_consecutive
    requirements = td_reqs_minimal_with_prereqs

    return workers, rotations, weeks, requirements


@pytest.fixture(scope="session")
def td_rotations_purple_must_be_succeeded_by_hosp():
    rotations = {
        "Purple HS Senior": {
            "min_workers_assigned": 0,
            "max_workers_assigned": 1,
        },
        "SHMC Hospitalist": {"min_workers_assigned": 0, "max_workers_assigned": 2},
        "Vacation": {"max_workers_assigned": 6},
    }
    return rotations


@pytest.fixture(scope="session")
def td_reqs_for_must_be_succeeded_test():
    """
    Note rotation to succeed a requirement must be specified as rotation name, not requirement.

    FUTURE: Could change to match against requirements, but this would require look up architecture which could outrun its usefulness.
    """
    requirements = {
        "R2 Base": {
            "HS Admitting Senior": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 4,
                    "must_be_succeeded_by": ["SHMC Hospitalist"],
                },
                "fulfilled_by": [
                    "Purple HS Senior",
                ],
            },
            "Hospitalist": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 4,
                },
                "fulfilled_by": ["SHMC Hospitalist"],
            },
            "Vacation": {"constraints": {"max_weeks": 3}, "fulfilled_by": ["Vacation"]},
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }
    return requirements


@pytest.fixture(scope="session")
def td_reqs_for_week_availability_test():
    requirements = {
        "R2 Base": {
            "HS Admitting Senior": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 4,
                },
                "fulfilled_by": [
                    "Purple HS Senior",
                ],
            },
            "Systems of Medicine": {
                "constraints": {"min_weeks": 1, "max_weeks": 1},
                "fulfilled_by": ["Systems of Medicine"],
            },
            "Vacation": {"constraints": {"max_weeks": 3}, "fulfilled_by": ["Vacation"]},
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }
    return requirements


@pytest.fixture(scope="session")
def td_rots_for_unavailable_weeks_test():
    rotations = {
        "Purple HS Senior": {
            "min_workers_assigned": 1,
            "max_workers_assigned": 1,
        },
        "Systems of Medicine": {
            "unavailable_weeks": [
                datetime.date(2026, 7, 6),
                datetime.date(2026, 7, 13),  # leaving 2026-07-20 available
                datetime.date(2026, 7, 27),  # leaving 2026-08-04
                datetime.date(2026, 8, 11),
            ]
        },
        "Vacation": {},
    }
    return rotations


@pytest.fixture(scope="session")
def td_rots_for_available_weeks_test():
    rotations = {
        "Purple HS Senior": {
            "min_workers_assigned": 1,
            "max_workers_assigned": 1,
        },
        "Systems of Medicine": {
            "available_weeks": [
                datetime.date(2026, 7, 6),
                datetime.date(2026, 7, 27),
            ]
        },
        "Vacation": {},
    }
    return rotations


@pytest.fixture(scope="session")
def td_rots_for_respect_block_alignment_test():
    rotations = {
        "Green HS Senior": {
            "min_workers_assigned": 1,
            "max_workers_assigned": 1,
        },
        "Orange HS Senior": {
            "min_workers_assigned": 1,
            "max_workers_assigned": 1,
        },
        "POCUS Elective": {"max_workers_assigned": 1},
        "Vacation": {},
    }
    return rotations


@pytest.fixture(scope="session")
def td_reqs_for_respect_block_alignment_test():
    requirements = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 4,
                    "min_contiguity": 2,
                    "must_respect_block_alignment": True,
                },
                "fulfilled_by": [
                    "Green HS Senior",
                    "Orange HS Senior",
                ],
            },
            "POCUS Elective": {
                "constraints": {"min_weeks": 0, "max_weeks": 2},
                "fulfilled_by": ["POCUS Elective"],
            },
            "Vacation": {"constraints": {"max_weeks": 3}, "fulfilled_by": ["Vacation"]},
        },
        "R2 PCT": {},
        "R2 Standard": {},
    }
    return requirements


@pytest.fixture(scope="session")
def minimal_must_be_succeeded_by_case(
    td_workers_three_simple: pl.DataFrame,
    td_weeks_six_consecutive: pl.DataFrame,
    td_rotations_purple_must_be_succeeded_by_hosp: dict[str, dict],
    td_reqs_for_must_be_succeeded_test: dict[str, dict],
):
    workers = td_workers_three_simple
    weeks = td_weeks_six_consecutive
    rotations = td_rotations_purple_must_be_succeeded_by_hosp
    requirements = td_reqs_for_must_be_succeeded_test
    return workers, rotations, weeks, requirements


@pytest.fixture(scope="session")
def minimal_unavailable_weeks(
    td_workers_three_simple: pl.DataFrame,
    td_weeks_six_consecutive: pl.DataFrame,
    td_rots_for_unavailable_weeks_test: dict[str, dict],
    td_reqs_for_week_availability_test: dict[str, dict],
):
    workers = td_workers_three_simple
    weeks = td_weeks_six_consecutive
    rotations = td_rots_for_unavailable_weeks_test
    requirements = td_reqs_for_week_availability_test
    return workers, rotations, weeks, requirements


@pytest.fixture(scope="session")
def minimal_available_weeks(
    td_workers_three_simple: pl.DataFrame,
    td_weeks_six_consecutive: pl.DataFrame,
    td_rots_for_available_weeks_test: dict[str, dict],
    td_reqs_for_week_availability_test: dict[str, dict],
):
    workers = td_workers_three_simple
    weeks = td_weeks_six_consecutive
    rotations = td_rots_for_available_weeks_test
    requirements = td_reqs_for_week_availability_test
    return workers, rotations, weeks, requirements


@pytest.fixture(scope="session")
def td_overrides_minimal():
    overrides = pl.DataFrame(
        [
            {
                "name": "Charles Chrysler",
                "monday_date": datetime.date(2026, 7, 6),
                "rotation": "Vacation",
                "override_value": True,
            },
            {
                "name": "Charles Chrysler",
                "monday_date": datetime.date(2026, 7, 20),
                "rotation": "Vacation",
                "override_value": True,
            },
            {
                "name": "Charles Chrysler",
                "monday_date": datetime.date(2026, 7, 13),
                "rotation": "Vacation",
                "override_value": False,
            },
        ]
    )
    return overrides


@pytest.fixture(scope="session")
def td_preferences_minimal():
    preferences = pl.DataFrame(
        [
            {
                "name": "Charles Chrysler",
                "monday_date": datetime.date(2026, 7, 13),
                "rotation": "Vacation",
                "preference": 10,
            },
            {  # intentional duplicate - should put him on Vacation and get 10
                "name": "Charles Chrysler",
                "monday_date": datetime.date(2026, 7, 13),
                "rotation": "Green HS Senior",
                "preference": -10,
            },
            {  # lesser request strength should lose to Charles
                "name": "Aaron Aaronson",
                "monday_date": datetime.date(2026, 7, 13),
                "rotation": "Vacation",
                "preference": 8,
            },
            {
                "name": "Bill Byornsen",
                "monday_date": datetime.date(2026, 7, 13),
                "rotation": "Green HS Senior",
                "preference": 3,
            },
        ]
    )
    return preferences


@pytest.fixture(scope="session")
def minimal_with_overrides(
    td_workers_three_simple: pl.DataFrame,
    td_weeks_six_consecutive: pl.DataFrame,
    td_rotations_gn_prp_vacation: dict[str, dict],
    td_reqs_minimal_with_prereqs: dict[str, dict],
    td_overrides_minimal: pl.DataFrame,
):
    workers = td_workers_three_simple
    weeks = td_weeks_six_consecutive
    rotations = td_rotations_gn_prp_vacation
    requirements = td_reqs_minimal_with_prereqs
    overrides = td_overrides_minimal
    return workers, rotations, weeks, requirements, overrides


@pytest.fixture(scope="session")
def minimal_with_respect_block_alignment(
    td_workers_four_simple: pl.DataFrame,
    td_weeks_eight_consecutive: pl.DataFrame,
    td_rots_for_respect_block_alignment_test: dict[str, dict],
    td_reqs_for_respect_block_alignment_test: dict[str, dict],
):
    workers = td_workers_four_simple
    weeks = td_weeks_eight_consecutive
    rotations = td_rots_for_respect_block_alignment_test
    requirements = td_reqs_for_respect_block_alignment_test
    return workers, rotations, weeks, requirements


@pytest.fixture(scope="session")
def minimal_with_preferences_case(
    td_workers_three_simple: pl.DataFrame,
    td_weeks_six_consecutive: pl.DataFrame,
    td_rotations_gn_prp_vacation: dict[str, dict],
    td_reqs_minimal_with_min_contiguity: dict[str, dict],
    td_preferences_minimal: pl.DataFrame,
):
    workers = td_workers_three_simple
    weeks = td_weeks_six_consecutive
    rotations = td_rotations_gn_prp_vacation
    requirements = td_reqs_minimal_with_min_contiguity
    overrides = None
    preferences = td_preferences_minimal
    return workers, rotations, weeks, requirements, overrides, preferences


@pytest.fixture(scope="session")
def real_2025_case_constraints_only():
    workers = pl.DataFrame(
        [
            {"name": "JBe", "track": "Standard", "year": "R3"},
            {"name": "JKa", "track": "Standard", "year": "R3"},
            {"name": "NKi", "track": "PCT", "year": "R3"},
            {"name": "BLe", "track": "PCT", "year": "R3"},
            {"name": "SNe", "track": "PCT", "year": "R3"},
            {"name": "IOl", "track": "PCT", "year": "R3"},
            {"name": "ASc", "track": "Standard", "year": "R3"},
            {"name": "TSe", "track": "Standard", "year": "R3"},
            {"name": "LSz", "track": "Standard", "year": "R3"},
            {"name": "EBr", "track": "Standard", "year": "R3"},
            {"name": "MAd", "track": "Standard", "year": "R2"},
            {"name": "JAz", "track": "Standard", "year": "R2"},
            {"name": "NBr", "track": "Standard", "year": "R2"},
            {"name": "ACh", "track": "Standard", "year": "R2"},
            {"name": "CGo", "track": "PCT", "year": "R2"},
            {"name": "AKa", "track": "Standard", "year": "R2"},
            {"name": "CLe", "track": "Standard", "year": "R2"},
            {"name": "CLo", "track": "Standard", "year": "R2"},
            {"name": "ASw", "track": "Standard", "year": "R2"},
            {"name": "AWe", "track": "PCT", "year": "R2"},
        ]
    )
    rotations = {
        "Green HS Senior": {
            "minimum_residents_assigned": 1,
            "maximum_residents_assigned": 1,
        },
        "Orange HS Senior": {
            "minimum_residents_assigned": 1,
            "maximum_residents_assigned": 1,
        },
        "Consults": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 2,
        },
        "SHMC ICU Senior": {
            "minimum_residents_assigned": 1,
            "maximum_residents_assigned": 1,
        },
        "SHMC CICU": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 1,
        },
        "Night Senior": {
            "minimum_residents_assigned": 1,
            "maximum_residents_assigned": 1,
        },
        "STHC Senior": {
            "minimum_residents_assigned": 1,
            "maximum_residents_assigned": 6,
        },
        "Vacation": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 30,
        },
        "Systems of Medicine": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 7,
        },
        "IP Cardiology Senior": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 1,
        },
        "Geriatrics": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 2,
        },
        "OP Cardiology": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 2,
        },
        "Psych Consult": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 1,
        },
        "Dermatology": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 2,
        },
        "Elective": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 30,
        },
        "GIM": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 10,
        },
        "Hospitalist": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 3,
        },
        "OP Pulmonology": {
            "minimum_residents_assigned": 0,
            "maximum_residents_assigned": 2,
        },
    }
    weeks = pl.DataFrame(
        [
            {"monday_date": "2026-07-06", "week": 1, "block": 1},
            {"monday_date": "2026-07-13", "week": 2, "block": 1},
            {"monday_date": "2026-07-20", "week": 3, "block": 1},
            {"monday_date": "2026-07-27", "week": 4, "block": 1},
            {"monday_date": "2026-08-03", "week": 5, "block": 2},
            {"monday_date": "2026-08-10", "week": 6, "block": 2},
            {"monday_date": "2026-08-17", "week": 7, "block": 2},
            {"monday_date": "2026-08-24", "week": 8, "block": 2},
            {"monday_date": "2026-08-31", "week": 9, "block": 3},
            {"monday_date": "2026-09-07", "week": 10, "block": 3},
            {"monday_date": "2026-09-14", "week": 11, "block": 3},
            {"monday_date": "2026-09-21", "week": 12, "block": 3},
            {"monday_date": "2026-09-28", "week": 13, "block": 4},
            {"monday_date": "2026-10-05", "week": 14, "block": 4},
            {"monday_date": "2026-10-12", "week": 15, "block": 4},
            {"monday_date": "2026-10-19", "week": 16, "block": 4},
            {"monday_date": "2026-10-26", "week": 17, "block": 5},
            {"monday_date": "2026-11-02", "week": 18, "block": 5},
            {"monday_date": "2026-11-09", "week": 19, "block": 5},
            {"monday_date": "2026-11-16", "week": 20, "block": 5},
            {"monday_date": "2026-11-23", "week": 21, "block": 6},
            {"monday_date": "2026-11-30", "week": 22, "block": 6},
            {"monday_date": "2026-12-07", "week": 23, "block": 6},
            {"monday_date": "2026-12-14", "week": 24, "block": 6},
            {"monday_date": "2026-12-21", "week": 25, "block": 7},
            {"monday_date": "2026-12-28", "week": 26, "block": 7},
            {"monday_date": "2027-01-04", "week": 27, "block": 7},
            {"monday_date": "2027-01-11", "week": 28, "block": 7},
            {"monday_date": "2027-01-18", "week": 29, "block": 8},
            {"monday_date": "2027-01-25", "week": 30, "block": 8},
            {"monday_date": "2027-02-01", "week": 31, "block": 8},
            {"monday_date": "2027-02-08", "week": 32, "block": 8},
            {"monday_date": "2027-02-15", "week": 33, "block": 9},
            {"monday_date": "2027-02-22", "week": 34, "block": 9},
            {"monday_date": "2027-03-01", "week": 35, "block": 9},
            {"monday_date": "2027-03-08", "week": 36, "block": 9},
            {"monday_date": "2027-03-15", "week": 37, "block": 10},
            {"monday_date": "2027-03-22", "week": 38, "block": 10},
            {"monday_date": "2027-03-29", "week": 39, "block": 10},
            {"monday_date": "2027-04-05", "week": 40, "block": 10},
            {"monday_date": "2027-04-12", "week": 41, "block": 11},
            {"monday_date": "2027-04-19", "week": 42, "block": 11},
            {"monday_date": "2027-04-26", "week": 43, "block": 11},
            {"monday_date": "2027-05-03", "week": 44, "block": 11},
            {"monday_date": "2027-05-10", "week": 45, "block": 12},
            {"monday_date": "2027-05-17", "week": 46, "block": 12},
            {"monday_date": "2027-05-24", "week": 47, "block": 12},
            {"monday_date": "2027-05-31", "week": 48, "block": 12},
            {"monday_date": "2027-06-07", "week": 49, "block": 13},
            {"monday_date": "2027-06-14", "week": 50, "block": 13},
            {"monday_date": "2027-06-21", "week": 51, "block": 13},
            {"monday_date": "2027-06-28", "week": 52, "block": 13},
        ]
    )
    requirements = {
        "R2 Base": {
            "HS Rounding Senior": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 4,
                    "min_contiguity": 2,
                    "max_contiguity": 4,
                    "must_respect_block_alignment": True,
                    "prerequisite": {
                        "weeks": 2,
                        "rots_meeting_prereqs": ["Purple HS Senior"],
                    },
                },
                "fulfilled_by": ["Green HS Senior", "Orange HS Senior"],
            },
            "HS Admitting Senior": {
                "constraints": {
                    "min_weeks": 5,
                    "max_weeks": 6,
                    "min_contiguity": 2,
                },
                "fulfilled_by": ["Purple HS Senior"],
            },
            "Night Senior": {
                "constraints": {
                    "min_weeks": 4,
                    "max_weeks": 4,
                    "min_contiguity": 4,
                },
                "fulfilled_by": ["Night Senior"],
            },
            "ICU Senior": {
                "constraints": {
                    "min_weeks": 4,
                    "max_weeks": 4,
                    "min_contiguity": 4,
                },
                "fulfilled_by": ["SHMC ICU Senior"],
            },
            "Consults": {
                "constraints": {
                    "min_weeks": 4,
                },
                "fulfilled_by": ["Consults"],
            },
            "Hospitalist": {
                "constraints": {
                    "max_weeks": 0,
                },
                "fulfilled_by": ["Hospitalist"],
            },
            "Vacation": {
                "constraints": {"min_weeks": 3, "max_weeks": 3},
                "fulfilled_by": ["Vacation"],
            },
            "STHC Senior": {
                "constraints": {
                    "max_weeks": 4,
                    "min_contiguity": 4,
                    "must_respect_block_alignment": True,
                },
                "fulfilled_by": ["STHC Senior"],
            },
            "OP Cardiology": {
                "constraints": {
                    "max_weeks": 4,
                    "min_contiguity": 2,
                },
                "fulfilled_by": ["OP Cardiology"],
            },
            "Dermatology": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 2,
                    "min_contiguity": 2,
                },
                "fulfilled_by": ["Dermatology"],
            },
            "Geriatrics": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 2,
                    "min_contiguity": 2,
                },
                "fulfilled_by": ["Geriatrics"],
            },
            "Psych Consult": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 2,
                    "min_contiguity": 2,
                },
                "fulfilled_by": ["Psych Consult"],
            },
            "Systems of Medicine": {
                "constraints": {
                    "min_weeks": 2,
                    "max_weeks": 2,
                    "min_contiguity": 2,
                },
                "fulfilled_by": ["Systems of Medicine"],
            },
            "Elective": {
                "constraints": {
                    "max_weeks": 20,
                },
                "fulfilled_by": ["Elective"],
            },
            "GIM": {
                "constraints": {
                    "max_weeks": 0,
                },
                "fulfilled_by": ["GIM"],
            },
        },
        "R2 Standard": {},
        "R2 PCT": {
            "GIM": {
                "constraints": {
                    "min_weeks": 4,
                    "max_weeks": 4,
                    "min_contiguity": 2,
                    "max_contiguity": 2,
                },
                "fulfilled_by": ["GIM"],
            }
        },
        "R3 Base": {
            "HS Rounding Senior": {
                "constraints": {
                    "min_weeks": 8,
                    "max_weeks": 4,
                    "min_contiguity": 2,
                    "max_contiguity": 4,
                    "must_respect_block_alignment": True,
                },
                "fulfilled_by": ["Green HS Senior", "Orange HS Senior"],
            },
            "Night Senior": {
                "constraints": {
                    "min_weeks": 1,
                    "max_weeks": 2,
                },
                "fulfilled_by": ["Night Senior"],
            },
            "Hospitalist": {
                "constraints": {
                    "min_weeks": 4,
                },
                "fulfilled_by": ["Hospitalist"],
            },
            "IP Cardiology": {
                "constraints": {
                    "min_weeks": 4,
                    "min_contiguity": 2,
                },
                "fulfilled_by": ["IP Cardiology"],
            },
            "OP Pulmonology": {
                "constraints": {
                    "min_weeks": 4,
                    "max_weeks": 8,
                    "min_contiguity": 2,
                },
                "fulfilled_by": ["OP Pulmonology"],
            },
            "Elective": {
                "constraints": {
                    "max_weeks": 20,
                },
                "fulfilled_by": ["Elective"],
            },
            "Vacation": {
                "constraints": {
                    "min_weeks": 4,
                    "max_weeks": 4,
                    "max_contiguity": 1,
                },
                "fulfilled_by": ["Elective"],
            },
            "OP Cardiology": {
                "constraints": {
                    "max_weeks": 0,
                },
                "fulfilled_by": ["Elective"],
            },
            "Systems of Medicine": {
                "constraints": {
                    "max_weeks": 0,
                },
                "fulfilled_by": ["Systems of Medicine"],
            },
        },
        "R3 Standard": {
            "STHC Senior": {
                "constraints": {
                    "min_weeks": 4,
                    "max_weeks": 4,
                    "min_contiguity": 4,
                    "max_contiguity": 4,
                    "must_respect_block_alignment": True,
                },
                "fulfilled_by": ["STHC Senior"],
            },
            "ICU Senior": {
                "constraints": {
                    "min_weeks": 4,
                    "max_weeks": 4,
                    "min_contiguity": 4,
                    "max_contiguity": 4,
                    "must_respect_block_alignment": True,
                },
                "fulfilled_by": ["SHMC ICU Senior", "SHMC CICU"],
            },
        },
        "R3 PCT": {
            "STHC Senior": {
                "constraints": {
                    "min_weeks": 8,
                    "max_weeks": 10,
                    "min_contiguity": 2,
                    "max_contiguity": 4,
                    "must_respect_block_alignment": True,
                },
                "fulfilled_by": ["STHC Senior"],
            },
            "GIM": {
                "constraints": {
                    "min_weeks": 4,
                    "max_weeks": 4,
                    "min_contiguity": 2,
                    "must_respect_block_alignment": True,
                },
                "fulfilled_by": ["GIM"],
            },
            "ICU Senior": {
                "constraints": {
                    "max_weeks": 0,
                },
                "fulfilled_by": ["ICU Senior", "SHMC CICU"],
            },
        },
    }

    return workers, rotations, weeks, requirements
