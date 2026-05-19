import polars as pl
import pytest

from data_io import generate_pl_wrapped_boolvar


@pytest.fixture
def minimal_case_setup():
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
                "minimum_residents_assigned": 1,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "Orange HS Senior",
                "requirement": "HS Rounding Senior",
                "minimum_residents_assigned": 1,
                "maximum_residents_assigned": 1,
            },
        ]
    )
    weeks = pl.DataFrame(
        [
            {"monday_date": "2026-07-06", "week": 1, "block": 1},
            {"monday_date": "2026-07-13", "week": 2, "block": 1},
            {"monday_date": "2026-07-20", "week": 3, "block": 1},
            {"monday_date": "2026-07-27", "week": 4, "block": 1},
        ]
    )

    return workers, rotations, weeks


@pytest.fixture
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
                "minimum_residents_assigned": 1,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "Orange HS Senior",
                "requirement": "HS Rounding Senior",
                "minimum_residents_assigned": 1,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "Purple HS Senior",
                "requirement": "HS Admitting Senior",
                "minimum_residents_assigned": 1,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "Consults",
                "requirement": "Consults",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 2,
            },
            {
                "rotation": "SHMC ICU Senior",
                "requirement": "ICU Senior",
                "minimum_residents_assigned": 1,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "SHMC CICU",
                "requirement": "ICU Senior",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "Night Senior",
                "requirement": "Night Senior",
                "minimum_residents_assigned": 1,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "STHC Senior",
                "requirement": "STHC Senior",
                "minimum_residents_assigned": 1,
                "maximum_residents_assigned": 2,
            },
            {
                "rotation": "Vacation",
                "requirement": "Vacation",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 30,
            },
            {
                "rotation": "Systems of Medicine",
                "requirement": "Systems of Medicine",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 7,
            },
            {
                "rotation": "IP Cardiology Senior",
                "requirement": "IP Cardiology Senior",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "Geriatrics",
                "requirement": "Geriatrics",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 2,
            },
            {
                "rotation": "OP Cardiology",
                "requirement": "OP Cardiology",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 2,
            },
            {
                "rotation": "Psych Consult",
                "requirement": "Psych Consult",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 1,
            },
            {
                "rotation": "Dermatology",
                "requirement": "Dermatology",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 2,
            },
            {
                "rotation": "Elective",
                "requirement": "Elective",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 30,
            },
            {
                "rotation": "GIM",
                "requirement": "GIM",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 4,
            },
            {
                "rotation": "Hospitalist",
                "requirement": "Hospitalist",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 3,
            },
            {
                "rotation": "OP Pulmonology",
                "requirement": "OP Pulmonology",
                "minimum_residents_assigned": 0,
                "maximum_residents_assigned": 2,
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
    )

    return workers, rotations, weeks


def test_generate_pl_wrapped_boolvar(minimal_case_setup):

    workers, rotations, weeks = minimal_case_setup

    wrapped = generate_pl_wrapped_boolvar(workers, rotations, weeks)

    assert isinstance(wrapped, pl.DataFrame)
    assert wrapped.shape[0] == len(workers) * len(rotations) * len(weeks)
