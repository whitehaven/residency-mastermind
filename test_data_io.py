import sys

import mergedeep
import polars as pl
import pytest
from loguru import logger

from data_io import compose_requirements_to_workers, generate_pl_wrapped_boolvar

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO"
)


def test_generate_pl_wrapped_boolvar(minimal_case_setup):
    workers, rotations, weeks, _requirements = minimal_case_setup

    wrapped = generate_pl_wrapped_boolvar(workers, rotations, weeks)

    assert isinstance(wrapped, pl.DataFrame)
    assert wrapped.shape[0] == len(workers) * len(rotations) * len(weeks)


def test_compose_requirements_to_workers(minimal_case_setup, minimal_req_composition):
    workers, _rotations, _weeks, _requirements = minimal_case_setup
    req_sets = minimal_req_composition

    workers_with_reqs = compose_requirements_to_workers(workers, req_sets)

    target_raw_data = pl.DataFrame(
        [
            {
                "name": "Aaron Aaronson",
                "req_set": {
                    "HS Rounding Senior": {
                        "constraints": {"min_weeks": 0, "max_weeks": 4},
                        "fulfilled_by": ["Green HS Senior", "Orange HS Senior"],
                    }
                },
                "year": "R2",
                "track": "Standard",
            },
            {
                "name": "Bill Byornsen",
                "req_set": {
                    "HS Rounding Senior": {
                        "constraints": {"min_weeks": 0, "max_weeks": 4},
                        "fulfilled_by": ["Green HS Senior", "Orange HS Senior"],
                    }
                },
                "year": "R2",
                "track": "PCT",
            },
        ]
    )

    assert workers_with_reqs.equals(target_raw_data)
