import yaml


def read_config_file(config_file_path: str | None = None) -> dict:
    default_file_path = "config.yaml"
    if config_file_path is None:
        config_file_path = default_file_path

    try:
        with open(config_file_path, "r") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file '{config_file_path}' was not found.")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
    return config


def write_config_file(config: dict, config_file_path: str | None = None) -> None:
    assert config is not None, "nothing to write"

    default_file_path = "config.yaml"
    if config_file_path is None:
        config_file_path = default_file_path

    try:
        with open(config_file_path, "w") as file:
            yaml.dump(data=config, stream=file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
    return None


def generate_default_config(config_file_path: str | None = None) -> dict:
    if config_file_path is None:
        config_file_path = "config.yaml"

    config = {
        "allowable_year_options": {"R2", "R3", "R3 Extended"},
        "cpmpy_variable_column": "is_scheduled_cp_var",
        "cpmpy_result_column": "is_scheduled_result",
        "residents_primary_label": "full_name",
        "rotations_primary_label": "rotation",
        "weeks_primary_label": "monday_date",
        "default_cpmpy_solver": "ortools",
        "testing_db_path": "seniors_only_anonymized.db",
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
                "full_year": "test_data/test_weeks_2025_2026_full.csv",
            },
        },
    }

    write_config_file(
        config,
        config_file_path=config_file_path,
    )

    print(f"(re)generated default config at {config_file_path}")

    return config


if __name__ == "__main__":
    generate_default_config()
