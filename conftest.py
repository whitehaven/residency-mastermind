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
