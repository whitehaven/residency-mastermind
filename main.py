import cpmpy as cp

from constraints import force_single_weekly_scheduling
from data_io import read_data_sqlite3, generate_pd_wrapped_boolvar


def main():
    input_tables = read_data_sqlite3("seniors_only.db")

    residents = input_tables["residents"]
    rotations = input_tables["rotations"]
    categories = input_tables["categories"]
    preferences = input_tables["preferences"]
    weeks = input_tables["weeks"]

    model = cp.Model()

    scheduled = generate_pd_wrapped_boolvar(residents, rotations, weeks)

    # TODO Constraints

    model += force_single_weekly_scheduling(residents, rotations, weeks, scheduled)

    # TODO Optimization

    # TODO Solve model

    model.solve("ortools", log_search_progress=True)

    # TODO Visualize


if __name__ == "__main__":
    main()
