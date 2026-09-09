import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    from data_io import generate_pl_wrapped_boolvar

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
    }
    weeks = pl.DataFrame(
        [
            {"monday_date": "2026-07-06", "week": 1, "block": 1},
            {"monday_date": "2026-07-13", "week": 2, "block": 1},
            {"monday_date": "2026-07-20", "week": 3, "block": 1},
            {"monday_date": "2026-07-27", "week": 4, "block": 1},
        ]
    )
    requirements = {
        "HS Rounding Senior": {
            "constraints": {
                "min_weeks_by_period": 2,
                "max_weeks_by_period": 4,
            },
        },
        "fulfilled_by": [
            "Green HS Senior",
            "Orange HS Senior",
        ],
    }
    return generate_pl_wrapped_boolvar, pl, rotations, weeks, workers


@app.cell
def _(generate_pl_wrapped_boolvar, rotations, weeks, workers):
    wrapped = generate_pl_wrapped_boolvar(workers, rotations, weeks)
    return (wrapped,)


@app.cell
def _(wrapped):
    wrapped
    return


@app.cell
def _(pl, wrapped):
    wrapped.group_by(["week"]).agg(pl.col("is_scheduled_cp_var").explode())
    return


@app.cell
def _(wrapped):
    type(wrapped["is_scheduled_cp_var"][0])
    return


@app.cell
def _(pl):
    def group_scheduled_df_by_for_each(
        subset_scheduled: pl.DataFrame,
        for_each_individual: list[str] | str,
        group_on_column: str,
    ) -> pl.DataFrame:
        """
        Get grouped subframes containing grouped decision variables by those fields which are "for each (individual)" when used for
        constraint generation. The returned grouped dataframe is thus siloed into groups which should be manipulated in iterated steps.

        Args:
            group_on_column: column to aggregate (either cpmpy_variable_column or cpmpy_result_column as found in config)
            subset_scheduled: pl.Dataframe subset from `scheduled` to set ranges along axes to place constraint
            for_each_individual: axis or axes to group by
        Returns:
            grouped pl.DataFrame

        Notes:
            Note any filtering should have happened before this as it will be hard to do now.

            I recognize this is essentially one line, but it's so syntactically weird I think it's worth leaving this way.

        Examples: The 1:1:1 constraint is "for each resident, for each week, for all rotations, sum of all should be ==
        1. In that case, for_each should receive `resident` and `week`. This means the `rotation` field is subject to
        constraint application and can then be processed in the next function.
        """
        assert group_on_column in subset_scheduled.columns, (
            f"{group_on_column} not in {subset_scheduled.columns}"
        )

        grouped = subset_scheduled.group_by(for_each_individual).agg(
            pl.col(group_on_column)
        )
        return grouped

    return (group_scheduled_df_by_for_each,)


@app.cell
def _(group_scheduled_df_by_for_each, wrapped):
    group_scheduled_df_by_for_each(
        subset_scheduled=wrapped,
        for_each_individual="name",
        group_on_column="is_scheduled_cp_var",
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
