# Objective Function Implementation for Residency Scheduling

This document describes the implementation of an objective function for the cpmpy-based residency scheduling model.

## Overview

The objective function allows the scheduler to optimize for resident preferences, vacation requests, and other scoring metrics while respecting all existing constraints. The implementation adds optimization capabilities to the existing constraint satisfaction framework.

## Key Features

### 1. Preference-Based Optimization
- **Positive scores**: Desired assignments (preferred rotations, vacation weeks)
- **Negative scores**: Undesired assignments (unwanted rotations, conflict weeks)
- **Zero scores**: Neutral assignments (no preference either way)

### 2. Flexible Preference Data Structure
```python
# DataFrame structure:
# resident, rotation, week, preference
pref_df = pl.DataFrame([
    ("Dr. Smith", "Elective", "2025-06-30", 10),   # Strongly preferred
    ("Dr. Smith", "Wards", "2025-06-30", -5),     # Strongly avoided
    ("Dr. Smith", "Clinic", "2025-06-30", 0),     # Neutral
], schema=["resident", "rotation", "week", "preference"])
```

### 3. Vacation and Request Support
- **Vacation requests**: High positive scores for vacation rotation during specific weeks
- **Rotation avoidance**: Negative scores for undesired rotations
- **Complex preferences**: Multiple preference types can be combined

## Implementation Details

### Core Functions

#### `create_preference_objective(scheduled, preferences)`
Creates a weighted sum objective from boolean variables and preference scores:
```python
objective = sum(boolvar * preference_score for each assignment)
```

#### `join_preferences_with_scheduled(scheduled, preferences)`
Merges preference scores with boolean variables by matching on resident, rotation, and week.

#### `calculate_total_preference_satisfaction(solved_schedule, preferences)`
Calculates the total preference score from a solved schedule for reporting.

#### `solve_with_optimization(model, objective)`
Solves the model with optimization rather than just feasibility checking.

### Integration Points

#### Main Function Updates
```python
# New optional parameters:
solve_schedule(
    residents, rotations, weeks,
    preferences=None,  # Preference DataFrame
    optimize=False     # Whether to optimize
)

# New command line arguments:
--optimize          # Enable optimization
--preferences FILE  # CSV file with preferences
```

## Usage Examples

### 1. Basic Optimization
```bash
python main.py -d schedule.db --optimize --preferences resident_prefs.csv
```

### 2. Vacation Requests
```python
# High positive score for vacation weeks
vacation_preferences = pl.DataFrame([
    ("Dr. Jones", "Vacation", "2025-07-07", 20),  # Wants vacation
    ("Dr. Jones", "Wards", "2025-07-07", -10),    # Avoid working
])
```

### 3. Rotation Preferences
```python
# Mixed preferences for different rotations
rotation_preferences = pl.DataFrame([
    ("Dr. Chen", "ICU", "2025-06-30", 8),     # Likes ICU
    ("Dr. Chen", "Elective", "2025-06-30", 15), # Prefers elective
    ("Dr. Chen", "Wards", "2025-06-30", -3),   # Dislikes wards
])
```

## Test Coverage

The implementation includes comprehensive test coverage:

### Core Function Tests
- ✅ `test_generate_blank_preferences_df()` - Basic preference DataFrame creation
- ✅ `test_join_preferences_with_scheduled()` - Data integration
- ✅ `test_create_preference_objective()` - Objective function creation
- ✅ `test_solve_with_optimization()` - Optimization solving

### Application Scenario Tests
- ✅ `test_vacation_optimization()` - Vacation request handling
- ✅ `test_complex_optimization_with_requirements()` - Multi-preference scenarios
- ✅ `test_optimization_improves_over_feasibility()` - Optimization benefits
- ✅ `test_minimal_preference_validity()` - Edge cases

### Test Fixtures
- Simple optimization setup (2 residents, 2 rotations, 2 weeks)
- Vacation request scenarios with mixed preferences
- Complex multi-resident, multi-preference scenarios

## Performance Considerations

### Memory Usage
- Objective function creates one term per resident×rotation×week combination
- Typical scheduling problem: ~50 residents × 15 rotations × 52 weeks = ~39,000 terms
- Well within cpmpy's handling capabilities

### Solving Time
- Optimization adds minimal overhead over constraint solving
- Most time spent in constraint satisfaction, not objective evaluation
- ortools solver efficiently handles linear objectives

## Integration with Existing System

### Compatibility
- ✅ All existing constraint functions remain unchanged
- ✅ Feasibility-only solving still available (default behavior)
- ✅ Existing test suite passes without modification
- ✅ Backward compatible with current scheduling workflow

### Migration Path
1. **Phase 1**: Deploy objective function alongside existing system
2. **Phase 2**: Add preference collection interfaces
3. **Phase 3**: Enable optimization by default for new schedules

## Future Enhancements

### Planned Features
1. **Priority-based preferences**: Hierarchical preference system
2. **Fairness constraints**: Ensure equitable preference satisfaction across residents
3. **Learning from past schedules**: ML-based preference prediction
4. **Multi-objective optimization**: Balance preferences with other metrics

### Extension Points
- Additional preference types (location, specific attendings, etc.)
- Constraint weighting (soft vs. hard constraints)
- Custom objective functions for different optimization goals

## Troubleshooting

### Common Issues

#### "No module named 'cpmpy'"
```bash
pip install cpmpy ortools
```

#### Solver not finding optimal solution
- Check for conflicting constraints
- Verify preference scores are reasonable
- Consider relaxing some constraints

#### Memory issues with large datasets
- Reduce time horizon
- Filter to essential residents/rotations
- Use chunked solving for very large problems

### Debug Tools
- Enable solver logging: `log_search_progress=True`
- Extract partial solutions during solving
- Use constraint debugging tools in cpmpy

## File Structure

```
├── optimization.py              # Core optimization functions
├── test_optimization.py         # Comprehensive test suite
├── main.py                    # Updated with optimization support
├── demo_optimization.py         # Example usage demonstration
└── README_objective.md         # This documentation
```

This implementation provides a robust, tested, and well-documented objective function that seamlessly integrates with the existing residency scheduling system while enabling powerful preference-based optimization capabilities.