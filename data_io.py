import cpmpy as cp
import mergedeep
import polars as pl
import yaml


def generate_pl_wrapped_boolvar(
    workers: pl.DataFrame, rotations: dict[str, dict], weeks: pl.DataFrame
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
    rotations_df = pl.DataFrame({"rotation": rotations.keys()})

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


def compose_requirements_to_workers(
    workers: pl.DataFrame, requirement_sets: dict[str, dict]
) -> pl.DataFrame:
    workers_reqs = {}

    for worker in workers.iter_rows(named=True):
        this_workers_reqs = {}
        match worker["year"]:
            case "R2":
                this_workers_reqs.update(requirement_sets.get("R2 Base", {}))
                match worker["track"]:
                    case "PCT":
                        this_workers_reqs = mergedeep.merge(
                            this_workers_reqs,
                            requirement_sets["R2 PCT"],
                            strategy=mergedeep.Strategy.REPLACE,
                        )
                    case "Fellowship":
                        this_workers_reqs = mergedeep.merge(
                            this_workers_reqs,
                            requirement_sets.get("R2 Fellowship", {}),
                            strategy=mergedeep.Strategy.REPLACE,
                        )
                    case "Standard":
                        this_workers_reqs = mergedeep.merge(
                            this_workers_reqs,
                            requirement_sets.get("R2 Standard", {}),
                            strategy=mergedeep.Strategy.REPLACE,
                        )
                    case _:
                        raise RuntimeError(f"{worker['track']=} doesn't exist")
            case "R3":
                this_workers_reqs.update(requirement_sets.get("R3 Base", {}))
                match worker["track"]:
                    case "PCT":
                        this_workers_reqs = mergedeep.merge(
                            this_workers_reqs,
                            requirement_sets["R3 PCT"],
                            strategy=mergedeep.Strategy.REPLACE,
                        )
                    case "Fellowship":
                        this_workers_reqs = mergedeep.merge(
                            this_workers_reqs,
                            requirement_sets.get("R3 Fellowship", {}),
                            strategy=mergedeep.Strategy.REPLACE,
                        )
                    case "Standard":
                        this_workers_reqs = mergedeep.merge(
                            this_workers_reqs,
                            requirement_sets.get("R3 Standard", {}),
                            strategy=mergedeep.Strategy.REPLACE,
                        )
                    case _:
                        raise NotImplementedError(f"{worker['track']=} doesn't exist")
            case "R1":
                raise NotImplementedError("Don't plan to implement R1")
            case _:
                raise RuntimeError(f"{worker['year']=} doesn't exist")

        workers_reqs.update({worker["name"]: this_workers_reqs})

    workers_df_with_reqs = pl.DataFrame(
        {"name": workers_reqs.keys(), "req_set": workers_reqs.values()}
    ).join(workers, on="name")

    return workers_df_with_reqs


def dump_polars_df_to_yaml(df: pl.DataFrame) -> str:
    return yaml.dump(df.to_dicts())
