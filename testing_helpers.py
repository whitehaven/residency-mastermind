import numpy as np
import polars as pl

tester_residents = pl.DataFrame(
    {
        "full_name": ["Fake Person, MD", "Also Fake Person, MD"],
        "year": ["R3", "R3"],
        "role": ["IM-Senior", "IM-Senior"],
        "track": ["Hospitalist", "Primary Care Track"],
    }
)


tester_rotations = pl.DataFrame(
    {
        "rotation": ["Green HS Senior", "Orange HS Senior", "SHMC Consults"],
        "category": ["HS Rounding Senior", "HS Rounding Senior", "Hospitalist"],
        "required_role": ["Senior", "Senior", "Senior"],
        "minimum_weeks": [0, 0, 0],
        "maximum_weeks": [8, 8, 4],
        "minimum_residents_assigned": [1, 1, 0],
        "maximum_residents_assigned": [1, 1, 1],
        "minimum_contiguous_weeks": [2, 2, 1],
        "max_contiguous_weeks": [np.nan, np.nan, np.nan],
    }
)


tester_weeks = pl.DataFrame(
    {
        "monday_date": [
            "2025-06-23",
            "2025-06-30",
            "2025-07-07",
            "2025-07-14",
            "2025-07-21",
            "2025-07-28",
            "2025-08-04",
            "2025-08-11",
            "2025-08-18",
        ],
        "week": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "starting_academic_year": [
            2025,
            2025,
            2025,
            2025,
            2025,
            2025,
            2025,
            2025,
            2025,
        ],
        "ending_academic_year": [
            2026,
            2026,
            2026,
            2026,
            2026,
            2026,
            2026,
            2026,
            2026,
        ],
    }
).with_columns(pl.col("monday_date").str.to_date())


def get_resident_week_vars(
    scheduled: pl.DataFrame, resident_name: str, week_date
) -> list:
    """Get all rotation variables for a specific resident and week."""
    return scheduled.filter(
        (pl.col("resident") == resident_name) & (pl.col("week") == week_date)
    )["is_scheduled_cp_var"].to_list()


def get_rotation_week_vars(
    scheduled: pl.DataFrame, rotation_name: str, week_date
) -> list:
    """Get all resident variables for a specific rotation and week."""
    return scheduled.filter(
        (pl.col("rotation") == rotation_name) & (pl.col("week") == week_date)
    )["is_scheduled_cp_var"].to_list()


def get_resident_rotation_vars(
    scheduled: pl.DataFrame, resident_name: str, rotation_name: str
) -> list:
    """Get all week variables for a specific resident and rotation."""
    return scheduled.filter(
        (pl.col("resident") == resident_name) & (pl.col("rotation") == rotation_name)
    )["is_scheduled_cp_var"].to_list()
