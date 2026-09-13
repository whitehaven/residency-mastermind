import polars as pl
import pytest


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
def large_case_setup():
    workers = pl.DataFrame(
        [
            {"name": "Aaron Aaronson", "year": "R1", "track": "Standard"},
            {"name": "Bill Byornsen", "year": "R1", "track": "PCT"},
        ]
    )

    rotations = pl.DataFrame(
        [
            {
                "rotation": "Green HS Senior",
                "requirement": "HS Rounding Senior",
                "min_workers_assigned": 1,
                "max_workers_assigned": 1,
            },
            {
                "rotation": "Orange HS Senior",
                "requirement": "HS Rounding Senior",
                "min_workers_assigned": 1,
                "max_workers_assigned": 1,
            },
            {
                "rotation": "Purple HS Senior",
                "requirement": "HS Admitting Senior",
                "min_workers_assigned": 1,
                "max_workers_assigned": 1,
            },
            {
                "rotation": "Consults",
                "requirement": "Consults",
                "min_workers_assigned": 0,
                "max_workers_assigned": 2,
            },
            {
                "rotation": "SHMC ICU Senior",
                "requirement": "ICU Senior",
                "min_workers_assigned": 1,
                "max_workers_assigned": 1,
            },
            {
                "rotation": "SHMC CICU",
                "requirement": "ICU Senior",
                "min_workers_assigned": 0,
                "max_workers_assigned": 1,
            },
            {
                "rotation": "Night Senior",
                "requirement": "Night Senior",
                "min_workers_assigned": 1,
                "max_workers_assigned": 1,
            },
            {
                "rotation": "STHC Senior",
                "requirement": "STHC Senior",
                "min_workers_assigned": 1,
                "max_workers_assigned": 2,
            },
            {
                "rotation": "Vacation",
                "requirement": "Vacation",
                "min_workers_assigned": 0,
                "max_workers_assigned": 30,
            },
            {
                "rotation": "Systems of Medicine",
                "requirement": "Systems of Medicine",
                "min_workers_assigned": 0,
                "max_workers_assigned": 7,
            },
            {
                "rotation": "IP Cardiology Senior",
                "requirement": "IP Cardiology Senior",
                "min_workers_assigned": 0,
                "max_workers_assigned": 1,
            },
            {
                "rotation": "Geriatrics",
                "requirement": "Geriatrics",
                "min_workers_assigned": 0,
                "max_workers_assigned": 2,
            },
            {
                "rotation": "OP Cardiology",
                "requirement": "OP Cardiology",
                "min_workers_assigned": 0,
                "max_workers_assigned": 2,
            },
            {
                "rotation": "Psych Consult",
                "requirement": "Psych Consult",
                "min_workers_assigned": 0,
                "max_workers_assigned": 1,
            },
            {
                "rotation": "Dermatology",
                "requirement": "Dermatology",
                "min_workers_assigned": 0,
                "max_workers_assigned": 2,
            },
            {
                "rotation": "Elective",
                "requirement": "Elective",
                "min_workers_assigned": 0,
                "max_workers_assigned": 30,
            },
            {
                "rotation": "GIM",
                "requirement": "GIM",
                "min_workers_assigned": 0,
                "max_workers_assigned": 4,
            },
            {
                "rotation": "Hospitalist",
                "requirement": "Hospitalist",
                "min_workers_assigned": 0,
                "max_workers_assigned": 3,
            },
            {
                "rotation": "OP Pulmonology",
                "requirement": "OP Pulmonology",
                "min_workers_assigned": 0,
                "max_workers_assigned": 2,
            },
        ]
    )
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
    ).with_columns(pl.col("monday_date").str.to_date())

    raise NotImplementedError("no requirements assembled")
    requirements = None

    return workers, rotations, weeks, requirements
