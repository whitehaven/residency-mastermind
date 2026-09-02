import cpmpy as cp
import polars as pl
import yaml


def generate_pl_wrapped_boolvar(
    workers: pl.DataFrame, rotations: dict[str,dict], weeks: pl.DataFrame
) -> pl.DataFrame:
    """
    Generate a Polars DataFrame wrapper around 3D CP-SAT boolean variables.

    Args:
        workers: df of workers (can get from DataFrame[<namecol>].to_list())
        rotations: k->v rotations
        weeks: df of weeks

    Returns:
        pl.DataFrame `scheduled`: wrapped around 3D array of workers, rotations, weeks
        for ease of complex indexing by string variables.
    """
    rotations_df = pl.DataFrame({"rotation":rotations.keys()})

    combinations = workers.join(rotations_df, how="cross").join(weeks, how="cross")

    variable_labels = [
        f"boolvar@({combo['name']}, {combo['rotation']}, {combo['monday_date']})"
        for combo in combinations.iter_rows(named=True)
    ]

    scheduled_vars = cp.boolvar(
        shape=(len(workers) * len(rotations) * len(weeks)),
        name=variable_labels,
    )

    scheduled = combinations.with_columns(
        pl.Series("is_scheduled_cp_var", scheduled_vars)
    )

    return scheduled


def dump_polars_df_to_yaml(df: pl.DataFrame) -> str:
    return yaml.dump(df.to_dicts())
