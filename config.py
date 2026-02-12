ALLOWABLE_YEAR_OPTIONS = {"R2", "R3", "R3 Extended"}
BLOCK_SCHEDULE_INDEX = "resident"
CPMPY_VARIABLE_COLUMN = "is_scheduled_cp_var"
CPMPY_RESULT_COLUMN = "is_scheduled_result"
RESIDENTS_PRIMARY_LABEL = "full_name"
ROTATIONS_PRIMARY_LABEL = "rotation"
WEEKS_PRIMARY_LABEL = "monday_date"
DEFAULT_CPMPY_SOLVER = "ortools"
DEFAULT_REQUIREMENTS_PATH = "requirements.yaml"
TESTING_DB_PATH = "seniors_only_anonymized_current_reqs.db"
TESTING_FILES = {
    "residents": {
        "tiny": "test_data/test_residents_tiny.csv",
        "real_size_seniors": "test_data/test_residents_real_size.csv",
        "only_R3s": "test_data/test_residents_real_size_R3_only.csv",
    },
    "rotations": {
        "tiny": "test_data/test_rotations_minimal.csv",
        "real_size": "test_data/test_rotations_real_size.csv",
    },
    "weeks": {
        "tiny": "test_data/test_weeks_tiny_10wk.csv",
        "full_three_years": "test_data/test_weeks_2024_2027_three_years.csv",
        "full_academic_year_2025_2026": "test_data/test_weeks_2025_2026.csv",
    },
}
PAYOUTS = {"Vacation": 10}
REQUEST_PRIORITY_SCORES = {
    "high": {"preference": 15, "avoidance": -15},
    "medium": {"preference": 8, "avoidance": -8},
    "low": {"preference": 3, "avoidance": -3},
}
SOLVER_TIME_LIMIT_S = 30
