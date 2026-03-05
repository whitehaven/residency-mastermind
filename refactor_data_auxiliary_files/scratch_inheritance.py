import mergedeep

fake_yaml = {
    "Consults": {
        "constraints": [
            {"resident_years": ["R2"], "type": "min_by_period", "weeks": 4}
        ],
        "fulfilled_by": ["Consults"],
    },
    "Dermatology": {
        "constraints": [
            {"resident_years": ["R2"], "type": "exact_by_period", "weeks": 2},
            {"resident_years": ["R2"], "type": "min_contiguity_in_period", "weeks": 2},
        ],
        "fulfilled_by": ["Dermatology"],
    },
}
more_specific = {
    "Consults": {
        "constraints": [{"type": "min_by_period", "weeks": 8}],
        "fulfilled_by": ["Consults"],
    },
}


output = mergedeep.merge(fake_yaml, more_specific, strategy=mergedeep.Strategy.REPLACE)


if __name__ == "__main__":

    import pprint

    pprint.pprint(output)
