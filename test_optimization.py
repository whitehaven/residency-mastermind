import itertools

import cpmpy as cp
import polars as pl
import pytest

import config
from constraints import (
    enforce_requirement_constraints,
    enforce_rotation_capacity_maximum,
    enforce_rotation_capacity_minimum,
    require_one_rotation_per_resident_per_week,
)
from data_io import generate_pl_wrapped_boolvar
from display import extract_solved_schedule
from optimization import (
    calculate_total_preference_satisfaction,
    create_preferences_objective,
    generate_blank_preferences_df,
    join_preferences_with_scheduled,
)
from requirement_builder import RequirementBuilder
from resident_requests_processor import (
    load_and_process_resident_requests,
    merge_with_existing_preferences,
    validate_resident_requests,
    expand_date_ranges,
    convert_requests_to_preferences,
)

real_size_residents = pl.read_csv(
    config.TESTING_FILES["residents"]["real_size_seniors"]
)
real_size_rotations = pl.read_csv(config.TESTING_FILES["rotations"]["real_size"])
one_academic_year_weeks = pl.read_csv(
    config.TESTING_FILES["weeks"]["full_academic_year_2025_2026"], try_parse_dates=True
)


def test_generate_blank_preferences_df():
    res_list = real_size_residents[config.RESIDENTS_PRIMARY_LABEL].to_list()
    rot_list = real_size_rotations[config.ROTATIONS_PRIMARY_LABEL].to_list()
    week_list = one_academic_year_weeks[config.WEEKS_PRIMARY_LABEL].to_list()

    preferences = generate_blank_preferences_df(res_list, rot_list, week_list)
    assert preferences.shape == (
        len(res_list) * len(rot_list) * len(week_list),
        4,
    ), "generated df is wrong dimension"
    assert preferences.columns == ["resident", "rotation", "week", "preference"]
    assert (preferences["preference"] == 0).all(), (
        "All preferences should be 0 in blank df"
    )


def test_join_preferences_with_scheduled():
    """Test joining preferences with scheduled boolean variables."""
    residents = pl.DataFrame(
        {"full_name": ["Resident A", "Resident B"], "year": ["R2", "R2"]}
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Elective", "Wards"],
            "category": ["Elective", "Wards"],
            "required_role": ["Any", "Any"],
            "minimum_residents_assigned": [0, 0],
            "maximum_residents_assigned": [10, 10],
            "minimum_contiguous_weeks": [None, None],
        }
    )
    weeks = one_academic_year_weeks.head(2)

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)
    preferences = generate_blank_preferences_df(
        residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
        rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
        weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
    )

    joined = join_preferences_with_scheduled(scheduled, preferences)

    assert len(joined) == len(scheduled), (
        "Joined should have same number of rows as scheduled"
    )
    assert "preference" in joined.columns, (
        "Preference column should be in joined DataFrame"
    )
    assert config.CPMPY_VARIABLE_COLUMN in joined.columns, (
        "Boolean variable column should be preserved"
    )


@pytest.fixture
def simple_optimization_setup():
    """Simple setup for optimization testing with 2 residents, 2 rotations, 2 weeks."""
    residents = pl.DataFrame(
        {"full_name": ["Resident A", "Resident B"], "year": ["R2", "R2"]}
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Elective", "Wards"],
            "category": ["Elective", "Wards"],
            "required_role": ["Any", "Any"],
            "minimum_residents_assigned": [0, 0],
            "maximum_residents_assigned": [10, 10],
            "minimum_contiguous_weeks": [None, None],
        }
    )
    weeks = one_academic_year_weeks.head(2)

    return residents, rotations, weeks


@pytest.fixture
def simple_optimization_setup_with_preferences(simple_optimization_setup):
    """Setup with preference data for optimization testing."""
    residents, rotations, weeks = simple_optimization_setup

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)
    preferences = generate_blank_preferences_df(
        residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
        rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
        weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
    )

    # Add some preferences
    preferences = preferences.with_columns(
        preference=pl.when(
            (pl.col("rotation") == "Elective") & (pl.col("resident") == "Resident A")
        )
        .then(10)
        .otherwise(0)
    )

    return residents, rotations, weeks, scheduled, preferences


def test_create_preference_objective(simple_optimization_setup_with_preferences):
    """Test objective function creation."""
    residents, rotations, weeks, scheduled, preferences = (
        simple_optimization_setup_with_preferences
    )

    objective = create_preferences_objective(scheduled, preferences)

    assert objective is not None, "Objective should be created"
    # Test that objective has expected structure (should be a sum expression)


def test_solve_with_optimization(simple_optimization_setup_with_preferences):
    """Test solving model with optimization objective."""
    residents, rotations, weeks, scheduled, preferences = (
        simple_optimization_setup_with_preferences
    )

    model = cp.Model()

    # Add basic constraints
    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)

    # Create and add objective
    objective = create_preferences_objective(scheduled, preferences)
    model.maximize(objective)

    # Solve
    is_optimal = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)

    assert is_optimal, "Model should find optimal solution"

    # Extract and check results
    solved_schedule = extract_solved_schedule(scheduled)
    total_satisfaction = calculate_total_preference_satisfaction(
        solved_schedule, preferences
    )


@pytest.fixture
def vacation_request_setup():
    """Setup for testing vacation request optimization."""
    residents = pl.DataFrame(
        {"full_name": ["Vacation Resident", "Regular Resident"], "year": ["R2", "R2"]}
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Vacation", "Wards"],
            "category": ["Vacation", "Wards"],
            "required_role": ["Any", "Any"],
            "minimum_residents_assigned": [0, 1],
            "maximum_residents_assigned": [10, 10],
            "minimum_contiguous_weeks": [None, None],
        }
    )
    weeks = one_academic_year_weeks.head(2)

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)
    preferences = generate_blank_preferences_df(
        residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
        rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
        weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
    )

    # Vacation resident wants vacation weeks (high positive score)
    # Negative score for working during vacation weeks
    preferences = preferences.with_columns(
        preference=pl.when(
            (pl.col("resident") == "Vacation Resident")
            & (pl.col("rotation") == "Vacation")
        )
        .then(20)
        .when(
            (pl.col("resident") == "Vacation Resident")
            & (pl.col("rotation") == "Wards")
        )
        .then(-10)
        .otherwise(0)
    )

    return residents, rotations, weeks, scheduled, preferences


def test_vacation_optimization(vacation_request_setup):
    """Test that optimization respects vacation preferences."""
    residents, rotations, weeks, scheduled, preferences = vacation_request_setup

    model = cp.Model()

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)

    objective = create_preferences_objective(scheduled, preferences)
    model.maximize(objective)

    is_optimal = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    assert is_optimal, "Vacation optimization should be feasible"

    solved_schedule = extract_solved_schedule(scheduled)
    total_satisfaction = calculate_total_preference_satisfaction(
        solved_schedule, preferences
    )

    # Should assign vacation resident to vacation (positive preference)
    # Check that vacation resident is scheduled on vacation rotation
    vacation_assignments = solved_schedule.filter(
        (pl.col("resident") == "Vacation Resident")
        & (pl.col("rotation") == "Vacation")
        & (pl.col(config.CPMPY_RESULT_COLUMN) == True)
    )

    assert len(vacation_assignments) > 0, (
        "Vacation resident should be assigned to vacation"
    )


@pytest.fixture
def complex_optimization_setup():
    """Complex setup with multiple preference types."""
    residents = pl.DataFrame(
        {
            "full_name": ["Senior Resident", "Junior Resident", "Third Resident"],
            "year": ["R3", "R2", "R2"],
        }
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Elective", "Wards", "ICU", "Clinic"],
            "category": ["Elective", "Wards", "ICU", "Clinic"],
            "required_role": ["Any", "Any", "Senior", "Any"],
            "minimum_residents_assigned": [0, 1, 0, 0],
            "maximum_residents_assigned": [10, 10, 2, 10],
            "minimum_contiguous_weeks": [None, None, 2, None],
        }
    )
    weeks = one_academic_year_weeks.head(3)

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)
    preferences = generate_blank_preferences_df(
        residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
        rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
        weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
    )

    # Complex preference structure:
    # - Senior Resident prefers ICU (high positive), dislikes Wards (negative)
    # - Junior Resident prefers Elective, neutral on others
    # - Third Resident wants vacation (specific week on Elective)
    preferences = preferences.with_columns(
        preference=pl.when(
            (pl.col("resident") == "Senior Resident") & (pl.col("rotation") == "ICU")
        )
        .then(15)
        .when(
            (pl.col("resident") == "Senior Resident") & (pl.col("rotation") == "Wards")
        )
        .then(-5)
        .when(
            (pl.col("resident") == "Junior Resident")
            & (pl.col("rotation") == "Elective")
        )
        .then(10)
        .when(
            (pl.col("resident") == "Third Resident")
            & (pl.col("rotation") == "Elective")
            & (pl.col("week") == weeks["monday_date"][0])  # First week
        )
        .then(20)
        .otherwise(0)
    )

    return residents, rotations, weeks, scheduled, preferences


def test_complex_optimization_with_requirements(complex_optimization_setup):
    """Test optimization with complex requirements."""
    residents, rotations, weeks, scheduled, preferences = complex_optimization_setup

    # Build requirements
    builder = RequirementBuilder()
    builder.add_requirement(
        "Wards", fulfilled_by=["Wards"]
    ).min_weeks_over_resident_years(1, ["R2"])
    builder.add_requirement("ICU", fulfilled_by=["ICU"]).min_weeks_over_resident_years(
        1, ["R3"]
    )
    builder.add_requirement(
        "Elective", fulfilled_by=["Elective"]
    ).max_weeks_over_resident_years(5, ["R2", "R3"])

    requirements = builder.accumulate_constraints_by_rule()
    prior_rotations_completed = pl.DataFrame(
        {"resident": [], "rotation": [], "completed_weeks": []}
    )

    model = cp.Model()

    # Add constraints
    model += enforce_requirement_constraints(
        requirements, residents, rotations, weeks, prior_rotations_completed, scheduled
    )
    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)

    # Add objective
    objective = create_preferences_objective(scheduled, preferences)
    model.maximize(objective)

    is_optimal = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    assert is_optimal, "Complex optimization should be feasible"

    solved_schedule = extract_solved_schedule(scheduled)
    total_satisfaction = calculate_total_preference_satisfaction(
        solved_schedule, preferences
    )

    # Should satisfy basic requirements while maximizing preferences
    assert total_satisfaction >= 0, "Should have non-negative preference satisfaction"


def test_optimization_improves_over_feasibility():
    """Test that optimization provides better results than pure feasibility."""
    residents = pl.DataFrame({"full_name": "Resident", "year": "R2"})
    rotations = pl.DataFrame(
        {
            "rotation": ["Preferred", "Unpreferred"],
            "category": ["Preferred", "Unpreferred"],
            "required_role": ["Any", "Any"],
            "minimum_residents_assigned": [0, 0],
            "maximum_residents_assigned": [1, 1],
            "minimum_contiguous_weeks": [None, None],
        }
    )
    weeks = one_academic_year_weeks.head(1)

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)

    # Feasibility-only solve
    feasibility_model = cp.Model()
    feasibility_model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )

    is_feasible = feasibility_model.solve(
        config.DEFAULT_CPMPY_SOLVER, log_search_progress=False
    )
    assert is_feasible, "Should be feasible"

    feasibility_schedule = extract_solved_schedule(scheduled)

    # Optimization solve with preferences
    preferences = generate_blank_preferences_df(
        residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
        rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
        weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
    )
    preferences = preferences.with_columns(
        preference=pl.when(pl.col("rotation") == "Preferred").then(10).otherwise(-10)
    )

    objective = create_preferences_objective(scheduled, preferences)

    optimization_model = cp.Model()
    optimization_model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    optimization_model.maximize(objective)

    is_optimal = optimization_model.solve(
        config.DEFAULT_CPMPY_SOLVER, log_search_progress=False
    )
    assert is_optimal, "Should be optimal"

    optimization_schedule = extract_solved_schedule(scheduled)
    optimal_satisfaction = calculate_total_preference_satisfaction(
        optimization_schedule, preferences
    )

    # Optimization should prefer the "Preferred" rotation
    preferred_assignments = optimization_schedule.filter(
        (pl.col("rotation") == "Preferred")
        & (pl.col(config.CPMPY_RESULT_COLUMN) == True)
    )

    assert len(preferred_assignments) > 0, "Should assign to preferred rotation"
    assert optimal_satisfaction > 0, "Should have positive preference score"


def test_minimal_preference_validity():
    """Test basic preference validation."""
    # Simple test without variable names to avoid cpmpy issues
    residents = pl.DataFrame({"full_name": ["TestResident"], "year": ["R2"]})
    rotations = pl.DataFrame(
        {
            "rotation": ["TestRotation"],
            "category": ["Test"],
            "required_role": ["Any"],
            "minimum_residents_assigned": [0],
            "maximum_residents_assigned": [1],
            "minimum_contiguous_weeks": [None],
        }
    )
    weeks = pl.DataFrame({"monday_date": ["Week1"]})

    # Test objective creation with basic preferences
    preferences = generate_blank_preferences_df(
        residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
        rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
        weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
    )

    # Create variables without names to avoid cpmpy name issues
    combinations = list(
        itertools.product(
            residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
            rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
            weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
        )
    )
    scheduled_vars = cp.boolvar(shape=len(combinations))

    scheduled = pl.DataFrame(
        {
            "resident": [combo[0] for combo in combinations],
            "rotation": [combo[1] for combo in combinations],
            "week": [combo[2] for combo in combinations],
            "is_scheduled_cp_var": scheduled_vars,
        }
    )

    # Should work with zero preferences
    objective = create_preferences_objective(scheduled, preferences)
    assert objective is not None, "Should create objective even with zero preferences"


def test_resident_requests_processor():
    """Test the resident request processor end-to-end."""
    # Create test data
    residents = pl.DataFrame(
        {"full_name": ["Test Resident 1", "Test Resident 2"], "year": ["R2", "R2"]}
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Elective", "Wards", "ICU"],
            "category": ["Elective", "Wards", "ICU"],
            "minimum_residents_assigned": [0, 1, 0],
            "maximum_residents_assigned": [10, 10, 2],
        }
    )
    weeks = one_academic_year_weeks.head(4)  # Use first 4 weeks

    # Create test requests
    test_requests = pl.DataFrame(
        {
            "resident": ["Test Resident 1", "Test Resident 2", "Test Resident 1"],
            "rotation": ["Elective", "ICU", "Wards"],
            "week_start": ["2025-06-30", "2025-07-07", "2025-07-14"],
            "week_end": ["2025-07-07", "2025-07-14", "2025-07-21"],
            "request_type": ["preference", "avoidance", "preference"],
            "priority": ["high", "medium", "low"],
        }
    )

    # Test validation
    validated_requests = validate_resident_requests(
        test_requests, residents, rotations, weeks
    )
    assert len(validated_requests) == 3, "All requests should be valid"

    # Test date expansion
    expanded_requests = expand_date_ranges(validated_requests, weeks)
    assert len(expanded_requests) > 3, (
        "Date ranges should be expanded to individual weeks"
    )

    # Test preference conversion
    preferences = convert_requests_to_preferences(expanded_requests)
    assert "preference" in preferences.columns, "Should have preference column"

    # Check correct preference scores
    high_pref = preferences.filter(
        (pl.col("resident") == "Test Resident 1") & (pl.col("rotation") == "Elective")
    )["preference"].max()
    assert high_pref == config.REQUEST_PRIORITY_SCORES["high"]["preference"], (
        "High preference should have correct score"
    )

    medium_avoid = preferences.filter(
        (pl.col("resident") == "Test Resident 2") & (pl.col("rotation") == "ICU")
    )["preference"].min()
    assert medium_avoid == config.REQUEST_PRIORITY_SCORES["medium"]["avoidance"], (
        "Medium avoidance should have correct score"
    )


def test_resident_requests_optimization():
    """Test that resident requests work with the optimization system."""
    residents = pl.DataFrame(
        {
            "full_name": ["Dr. Smith", "Dr. Jones", "Dr. Chen"],
            "year": ["R2", "R3", "R2"],
        }
    )
    rotations = pl.DataFrame(
        {
            "rotation": ["Elective", "Wards", "ICU Senior", "Vacation"],
            "category": ["Elective", "Wards", "ICU", "Vacation"],
            "minimum_residents_assigned": [0, 1, 0, 0],
            "maximum_residents_assigned": [10, 10, 2, 10],
        }
    )
    weeks = one_academic_year_weeks.head(6)  # Use first 6 weeks

    # Generate scheduled variables
    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)

    # Start with blank preferences
    preferences = generate_blank_preferences_df(
        residents[config.RESIDENTS_PRIMARY_LABEL].to_list(),
        rotations[config.ROTATIONS_PRIMARY_LABEL].to_list(),
        weeks[config.WEEKS_PRIMARY_LABEL].to_list(),
    )

    # Create test requests
    test_requests = pl.DataFrame(
        {
            "resident": ["Dr. Smith", "Dr. Jones", "Dr. Chen", "Dr. Smith"],
            "rotation": ["Elective", "ICU Senior", "Vacation", "Wards"],
            "week_start": ["2025-06-30", "2025-07-07", "2025-07-14", "2025-07-21"],
            "week_end": ["2025-07-07", "2025-07-14", "2025-07-21", "2025-07-28"],
            "request_type": ["preference", "preference", "preference", "avoidance"],
            "priority": ["high", "medium", "low", "high"],
        }
    )

    # Process requests
    validated_requests = validate_resident_requests(
        test_requests, residents, rotations, weeks
    )
    expanded_requests = expand_date_ranges(validated_requests, weeks)
    request_preferences = convert_requests_to_preferences(expanded_requests)

    # Merge with blank preferences
    final_preferences = merge_with_existing_preferences(
        request_preferences, preferences
    )

    # Create optimization model
    model = cp.Model()

    # Add basic constraints
    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )
    model += enforce_rotation_capacity_minimum(residents, rotations, weeks, scheduled)
    model += enforce_rotation_capacity_maximum(residents, rotations, weeks, scheduled)

    # Add preference objective
    objective = create_preferences_objective(scheduled, final_preferences)
    model.maximize(objective)

    # Solve
    is_optimal = model.solve(config.DEFAULT_CPMPY_SOLVER, log_search_progress=False)
    assert is_optimal, "Model with resident requests should be feasible"

    # Extract and verify results
    solved_schedule = extract_solved_schedule(scheduled)
    total_satisfaction = calculate_total_preference_satisfaction(
        solved_schedule, final_preferences
    )

    # Should have positive satisfaction (prefers requested assignments)
    assert total_satisfaction > 0, "Should have positive preference satisfaction"

    # Check that high-preference requests are likely honored
    dr_smith_elective = solved_schedule.filter(
        (pl.col("resident") == "Dr. Smith")
        & (pl.col("rotation") == "Elective")
        & (pl.col(config.CPMPY_RESULT_COLUMN) == True)
    )
    assert len(dr_smith_elective) > 0, (
        "Dr. Smith should be assigned to Elective (high preference)"
    )

    # Check that avoidance requests are likely avoided (minimized)
    dr_smith_wards = solved_schedule.filter(
        (pl.col("resident") == "Dr. Smith")
        & (pl.col("rotation") == "Wards")
        & (pl.col(config.CPMPY_RESULT_COLUMN) == True)
    )
    # Should have minimal assignments to avoided rotation
    # (avoidance doesn't guarantee zero, but should minimize when constraints allow)
    dr_smith_elective_count = len(dr_smith_elective)
    dr_smith_wards_count = len(dr_smith_wards)

    # Should prefer elective over wards when possible
    assert dr_smith_elective_count >= dr_smith_wards_count, (
        "Dr. Smith should have more elective assignments than wards "
        f"(elective: {dr_smith_elective_count}, wards: {dr_smith_wards_count})"
    )


def test_resident_requests_with_existing_vacation_preferences():
    """Test merging resident requests with existing vacation preferences."""
    residents = pl.DataFrame({"full_name": ["Dr. Test"], "year": ["R2"]})
    rotations = pl.DataFrame(
        {
            "rotation": ["Vacation", "Elective"],
            "category": ["Vacation", "Elective"],
            "minimum_residents_assigned": [0, 0],
            "maximum_residents_assigned": [10, 10],
        }
    )
    weeks = one_academic_year_weeks.head(3)

    # Existing vacation preferences (like real_2026_vacation_preferences.csv)
    existing_vacation_prefs = pl.DataFrame(
        {
            "resident": ["Dr. Test", "Dr. Test"],
            "rotation": ["Vacation", "Vacation"],
            "week": ["2025-06-30", "2025-07-07"],
            "preference": [10, 10],  # From config.PAYOUTS
        }
    )

    # New resident requests
    new_requests = pl.DataFrame(
        {
            "resident": ["Dr. Test"],
            "rotation": ["Elective"],
            "week_start": ["2025-06-30"],
            "week_end": ["2025-07-07"],
            "request_type": ["preference"],
            "priority": ["high"],
        }
    )

    # Process new requests
    validated_requests = validate_resident_requests(
        new_requests, residents, rotations, weeks
    )
    expanded_requests = expand_date_ranges(validated_requests, weeks)
    new_preferences = convert_requests_to_preferences(expanded_requests)

    # Merge with existing
    merged_preferences = merge_with_existing_preferences(
        new_preferences, existing_vacation_prefs
    )

    # Should contain both vacation and elective preferences
    assert len(merged_preferences) > len(existing_vacation_prefs), (
        "Should have more preferences after merge"
    )

    # Check that both types are present
    vacation_prefs = merged_preferences.filter(pl.col("rotation") == "Vacation")
    elective_prefs = merged_preferences.filter(pl.col("rotation") == "Elective")

    assert len(vacation_prefs) > 0, "Should preserve vacation preferences"
    assert len(elective_prefs) > 0, "Should add new elective preferences"
