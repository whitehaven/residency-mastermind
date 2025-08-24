import polars as pl


# TODO needs testing
def test_full_solution(solved_schedule: pl.DataFrame) -> dict:
    """
    Validate that the solution meets all constraints and provide summary stats.

    Args:
        solved_schedule: DataFrame with solved values

    Returns:
        Dictionary with validation results and stats
    """
    scheduled_only = solved_schedule.filter(pl.col("is_scheduled_value") == True)

    # Check one rotation per resident per week
    resident_week_counts = scheduled_only.group_by(["resident", "week"]).len()
    violations = resident_week_counts.filter(pl.col("len") > 1)

    # Summary statistics
    total_assignments = len(scheduled_only)
    unique_residents = scheduled_only["resident"].n_unique()
    unique_weeks = scheduled_only["week"].n_unique()
    unique_rotations = scheduled_only["rotation"].n_unique()

    # Assignments per resident
    assignments_per_resident = scheduled_only.group_by("resident").len().sort("len")

    return {
        "is_valid": len(violations) == 0,
        "constraint_violations": violations.to_dicts() if len(violations) > 0 else [],
        "total_assignments": total_assignments,
        "unique_residents_scheduled": unique_residents,
        "unique_weeks_covered": unique_weeks,
        "unique_rotations_used": unique_rotations,
        "assignments_per_resident": assignments_per_resident.to_dicts(),
    }
