import numpy as np
import polars as pl

from config import read_config_file

config = read_config_file()
cpmpy_variable_column = config["cpmpy_variable_column"]
cpmpy_result_column = config["cpmpy_result_column"]
default_solver = config["default_cpmpy_solver"]

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
