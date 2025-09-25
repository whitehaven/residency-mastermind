from config import config
from requirement_builder import (
    generate_builder_with_current_requirements,
    read_builder_polars_df_from_sqlite,
)


def test_read_builder_polars_df_from_sqlite():
    currently_accurate_requirements_builder = (
        generate_builder_with_current_requirements()
    )
    df_directly_from_builder = currently_accurate_requirements_builder.to_polars()

    currently_accurate_requirements_builder.write_polars_df_to_sqlite(
        config.testing_db_path
    )
    df_read_from_sql = read_builder_polars_df_from_sqlite(config.testing_db_path)

    assert df_directly_from_builder.equals(
        df_read_from_sql
    ), "df read back from sqlite != df generated from RequirementBuilder"
