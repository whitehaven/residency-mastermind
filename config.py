import box


def reset_to_default_config(config_file_path: str | None = "config.yaml") -> None:
    config = box.Box(
        {
            "allowable_year_options": {"R2", "R3", "R3 Extended"},
            "cpmpy_variable_column": "is_scheduled_cp_var",
            "cpmpy_result_column": "is_scheduled_result",
            "residents_primary_label": "full_name",
            "rotations_primary_label": "rotation",
            "weeks_primary_label": "monday_date",
            "default_cpmpy_solver": "ortools",
            "default_maximum_contiguity": 4,
            "testing_db_path": "seniors_only_anonymized_current_reqs.db",
            "testing_files": {
                "residents": {
                    "tiny": "test_data/test_residents_tiny.csv",
                    "real_size_seniors": "test_data/test_residents_real_size.csv",
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
            },
        }
    )
    config.to_yaml(config_file_path)


if __name__ == "__main__":
    reset_to_default_config()
