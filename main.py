import cpmpy as cp

from constraints import require_one_rotation_per_resident_per_week
from data_io import (
    read_bulk_data_sqlite3,
    generate_pl_wrapped_boolvar,
)
from display import extract_solved_schedule


def main():
    input_tables = read_bulk_data_sqlite3("seniors_only.db")

    residents = input_tables["residents"]
    rotations = input_tables["rotations"]
    categories = input_tables["categories"]
    preferences = input_tables["preferences"]
    weeks = input_tables["weeks"]

    model = cp.Model()

    scheduled = generate_pl_wrapped_boolvar(residents, rotations, weeks)

    # TODO Constraints

    model += require_one_rotation_per_resident_per_week(
        residents, rotations, weeks, scheduled
    )

    # TODO Optimization

    # TODO Solve model

    is_feasible = model.solve("ortools", log_search_progress=True)
    if not is_feasible:
        raise ValueError("Infeasible")

    # TODO Visualize
    solved_schedule = extract_solved_schedule(scheduled)
    print(solved_schedule)


if __name__ == "__main__":
    main()
