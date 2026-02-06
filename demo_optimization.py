#!/usr/bin/env python3
"""
Example script demonstrating objective function usage for residency scheduling.
"""

import argparse
import polars as pl

import config
from main import main


def create_sample_preferences():
    """Create a sample preferences CSV for testing."""

    # Sample data - this would normally come from resident preferences
    sample_preferences = [
        (
            "Resident A",
            "Elective",
            "2025-06-30",
            10,
        ),  # High preference for elective first week
        ("Resident A", "Wards", "2025-06-30", -5),  # Negative for wards same week
        (
            "Resident A",
            "Elective",
            "2025-07-07",
            8,
        ),  # Still high preference for elective
        ("Resident B", "Wards", "2025-06-30", 5),  # Positive for wards
        ("Resident B", "Elective", "2025-06-30", 2),  # Mild preference for elective
    ]

    preferences_df = pl.DataFrame(
        sample_preferences, schema=["resident", "rotation", "week", "preference"]
    )

    # Convert week to datetime
    preferences_df = preferences_df.with_columns(pl.col("week").str.to_date())

    return preferences_df


def demo_optimization():
    """Demonstrate optimization with preferences."""
    print("Creating sample preferences...")
    preferences = create_sample_preferences()

    # Save to CSV for main function to read
    preferences.write_csv("sample_preferences.csv")
    print("Saved preferences to sample_preferences.csv")

    # Create mock args for main function
    class MockArgs:
        def __init__(self):
            self.database = "test_data/seniors_only_anonymized_current_reqs.db"
            self.block_output = None
            self.optimize = True
            self.preferences = "sample_preferences.csv"

    print("\nRunning optimization with preferences...")
    try:
        solved_schedule = main(MockArgs())
        print(f"Optimization completed successfully!")
        print(f"Schedule shape: {solved_schedule.shape}")

        # Show some sample assignments
        sample_assignments = solved_schedule.filter(
            pl.col(config.CPMPY_RESULT_COLUMN) == True
        ).head(5)
        print("\nSample assignments:")
        print(sample_assignments.select("resident", "rotation", "week"))

    except Exception as e:
        print(f"Error during optimization: {e}")

    # Cleanup
    import os

    if os.path.exists("sample_preferences.csv"):
        os.remove("sample_preferences.csv")


if __name__ == "__main__":
    demo_optimization()
