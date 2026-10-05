import itertools as it

import cpmpy as cp
import polars as pl

import config


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
) -> int | cp.core.Operator:
    """
    Create a preference-based objective function for the scheduling model.

    It will be maximized, therefore higher is more likely to be respected.

    Args:
        scheduled: DataFrame with boolean variables
        preferences: DataFrame with preference scores

    Returns:
        cpmpy expression representing the objective to maximize

    Example:
        # High positive score for desired vacation week
        # Negative score for undesirable assignments
        # Zero score for neutral assignments
    """

    joined = join_preferences_with_scheduled(scheduled, preferences)

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
    """
    Calculate total preference satisfaction from a solved schedule.

    Args:
        solved_schedule: DataFrame with solved boolean results
        preferences: DataFrame with preference scores

    Returns:
        Total preference score (sum of preference * scheduled_boolean)
    """
    joined = solved_schedule.join(
        preferences, on=["resident", "rotation", "week"], how="inner"
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
