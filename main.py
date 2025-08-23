import cpmpy as cp

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

    # TODO Optimization

    # TODO Solve model
    # TODO visualize


if __name__ == "__main__":
    main()
