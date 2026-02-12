import sys
from datetime import datetime, timedelta

import polars as pl
from loguru import logger

import config

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)

def validate_resident_requests(
    requests_df: pl.DataFrame,
    residents_df: pl.DataFrame,
    rotations_df: pl.DataFrame,
    weeks_df: pl.DataFrame,
) -> pl.DataFrame:
    """
    Validate resident requests against existing data.

    Args:
        requests_df: DataFrame with resident requests
        residents_df: DataFrame with valid residents
        rotations_df: DataFrame with valid rotations
        weeks_df: DataFrame with valid weeks

    Returns:
        Validated requests DataFrame

    Raises:
        ValueError: If validation fails
    """
    valid_residents = residents_df[config.RESIDENTS_PRIMARY_LABEL].to_list() # TODO gotta be a better way for membership check
    valid_rotations = rotations_df[config.ROTATIONS_PRIMARY_LABEL].to_list()
    valid_weeks = weeks_df[config.WEEKS_PRIMARY_LABEL].to_list()

    errors = []

    for request in requests_df.iter_rows(named=True):
        if request["resident"] not in valid_residents:
            errors.append(f"Invalid resident: {request['resident']}")
        if request["rotation"] not in valid_rotations:
            errors.append(f"Invalid rotation: {request['rotation']}")

        # Check dates are valid and within academic year
        try:
            start_date = datetime.strptime(request["week_start"], "%Y-%m-%d").date()
            end_date = datetime.strptime(request["week_end"], "%Y-%m-%d").date()
        except ValueError:
            errors.append(
                f"Invalid date format: {request['week_start']} - {request['week_end']}"
            )
            continue

        if start_date > end_date:
            errors.append(
                f"Start date after end date: {request['week_start']} - {request['week_end']}"
            )

        if start_date < min(valid_weeks) or end_date > max(valid_weeks):
            errors.append(
                f"Date range outside academic year: {request['week_start']} - {request['week_end']}"
            )

        # Validate request type and priority
        if request["request_type"] not in ["preference", "avoidance"]:
            errors.append(f"Invalid request type: {request['request_type']}")

        if request["priority"] not in ["high", "medium", "low"]:
            errors.append(f"Invalid priority: {request['priority']}")

    if errors:
        logger.critical(f"Validation errors: {'; '.join(errors)}")
        raise ValueError(f"Validation errors: {'; '.join(errors)}")

    return requests_df


def expand_date_ranges(
    requests_df: pl.DataFrame, weeks_df: pl.DataFrame
) -> pl.DataFrame:
    """
    Expand date ranges to individual week assignments.

    Args:
        requests_df: DataFrame with date ranges
        weeks_df: DataFrame with week dates

    Returns:
        DataFrame with individual week assignments
    """
    expanded_rows = []

    # Get week mapping for efficient lookup - ensure we have string dates
    week_dates = weeks_df[config.WEEKS_PRIMARY_LABEL].cast(pl.Utf8).to_list()
    week_set = set(week_dates)

    for row in requests_df.iter_rows(named=True):
        start_date = datetime.strptime(row["week_start"], "%Y-%m-%d").date()
        end_date = datetime.strptime(row["week_end"], "%Y-%m-%d").date()

        # Generate week by week from start to end
        current_date = start_date
        while current_date <= end_date:
            week_str = current_date.strftime("%Y-%m-%d")

            # Only include if this week exists in our academic year
            if week_str in week_set:
                expanded_rows.append(
                    {
                        "resident": row["resident"],
                        "rotation": row["rotation"],
                        "week": week_str,
                        "request_type": row["request_type"],
                        "priority": row["priority"],
                    }
                )

            current_date += timedelta(days=7)  # Move to next week

    return pl.DataFrame(expanded_rows)


def convert_requests_to_preferences(expanded_requests: pl.DataFrame) -> pl.DataFrame:
    """
    Convert resident requests to preference scores.

    Args:
        expanded_requests: DataFrame with expanded weekly requests

    Returns:
        DataFrame with preference scores compatible with optimization system
    """
    # Handle priority mapping with when-then logic using config values
    preferences = expanded_requests.with_columns(
        preference=pl.when( # TODO I have to believe this could be done better than this with a join
            (pl.col("priority") == "high") & (pl.col("request_type") == "preference")
        )
        .then(config.REQUEST_PRIORITY_SCORES["high"]["preference"])
        .when((pl.col("priority") == "high") & (pl.col("request_type") == "avoidance"))
        .then(config.REQUEST_PRIORITY_SCORES["high"]["avoidance"])
        .when(
            (pl.col("priority") == "medium") & (pl.col("request_type") == "preference")
        )
        .then(config.REQUEST_PRIORITY_SCORES["medium"]["preference"])
        .when(
            (pl.col("priority") == "medium") & (pl.col("request_type") == "avoidance")
        )
        .then(config.REQUEST_PRIORITY_SCORES["medium"]["avoidance"])
        .when((pl.col("priority") == "low") & (pl.col("request_type") == "preference"))
        .then(config.REQUEST_PRIORITY_SCORES["low"]["preference"])
        .when((pl.col("priority") == "low") & (pl.col("request_type") == "avoidance"))
        .then(config.REQUEST_PRIORITY_SCORES["low"]["avoidance"])
        .otherwise(0)
    )

    # Select only the columns needed for preferences and ensure consistent types
    return preferences.select(
        ["resident", "rotation", "week", pl.col("preference").cast(pl.Int64)]
    )


def load_and_process_resident_requests(
    requests_path: str,
    residents_df: pl.DataFrame,
    rotations_df: pl.DataFrame,
    weeks_df: pl.DataFrame,
) -> pl.DataFrame:
    """
    Complete pipeline to load, validate, and process resident requests.

    Args:
        requests_path: Path to resident requests CSV
        residents_df: DataFrame with valid residents
        rotations_df: DataFrame with valid rotations
        weeks_df: DataFrame with valid weeks

    Returns:
        DataFrame with processed preferences ready for optimization
    """
    # Load requests
    requests_df = pl.read_csv(requests_path)

    # Validate requests
    validated_requests = validate_resident_requests(
        requests_df, residents_df, rotations_df, weeks_df
    )

    # Expand date ranges to individual weeks
    expanded_requests = expand_date_ranges(validated_requests, weeks_df)

    # Convert to preference scores
    preferences = convert_requests_to_preferences(expanded_requests)

    return preferences


def merge_with_existing_preferences(
    new_preferences: pl.DataFrame, existing_preferences: pl.DataFrame
) -> pl.DataFrame:
    """
    Merge new resident request preferences with existing preferences.
    New preferences override existing ones for the same resident/rotation/week combination.

    Args:
        new_preferences: DataFrame with new preference scores
        existing_preferences: DataFrame with existing preference scores

    Returns:
        Merged preferences DataFrame
    """
    # Ensure week columns have same type for joining
    existing_preferences_normalized = existing_preferences

    # Remove any existing entries that conflict with new preferences
    existing_filtered = existing_preferences_normalized.join(
        new_preferences.select(["resident", "rotation", "week"]),
        on=["resident", "rotation", "week"],
        how="anti",
    )

    # Combine existing (filtered) with new preferences
    merged = pl.concat([existing_filtered, new_preferences])

    return merged.sort(["resident", "rotation", "week"])
