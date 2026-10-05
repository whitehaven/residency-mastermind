import itertools as it

import cpmpy as cp
import polars as pl

import config

# hold on, could we not just tack a preferences column onto `scheduled`?


def generate_blank_preferences_df(
    resident_list: list, rotations_list: list, weeks_list: list
) -> pl.DataFrame:
    """
    Generate a blank preferences DataFrame with all preferences set to 0.

    Args:
        resident_list: List of resident names
        rotations_list: List of rotation names
        weeks_list: List of week dates

    Returns:
        DataFrame with columns: resident, rotation, week, preference
    """
    blank_preferences = pl.DataFrame(
        list(
            it.product(
                resident_list,
                rotations_list,
                weeks_list,
            )
        ),
        orient="row",
        schema=["resident", "rotation", "week"],
    )
    blank_preferences = blank_preferences.with_columns(preference=pl.lit(0))
    return blank_preferences


def create_preferences_objective(
    scheduled: pl.DataFrame, preferences: pl.DataFrame
) -> cp.core.Operator:

    joined = preferences.join(
        scheduled, on=["name", "monday_date", "rotation"], how="left"
    )

    # Create weighted sum: sum(boolvar * preference_score)
    objective_terms = []
    for row in joined.iter_rows(named=True):
        boolvar = row[config.CPMPY_VARIABLE_COLUMN]
        preference = row["preference"]
        objective_terms.append(boolvar * preference)

    if not objective_terms:
        return 0

    return cp.sum(objective_terms)


def calculate_total_preference_satisfaction(
    solved_schedule: pl.DataFrame, preferences: pl.DataFrame
) -> int:
    joined = solved_schedule.join(
        preferences, on=["name", "monday_date", "rotation"], how="left"
    )

    total_score = (
        joined.with_columns(
            weighted_score=pl.col(config.CPMPY_RESULT_COLUMN) * pl.col("preference")
        )
        .select("weighted_score")
        .sum()
        .item()
    )
    return total_score
