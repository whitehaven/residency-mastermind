from dataclasses import dataclass, field
from typing import Dict, List, Any

import polars as pl
from icecream import ic


@dataclass
class RequirementRule:

    name: str
    fulfilled_by: List[str]
    _constraints: List[Dict[str, Any]] = field(default_factory=list)

    def min_weeks_in_year(self, min_weeks: int, year: str):
        self._constraints.append(
            {"type": "min_by_period", "value": min_weeks, "filter": {"years": year}}
        )
        return self

    def max_weeks_in_year(self, max_weeks: int, year: str):
        self._constraints.append(
            {"type": "max_by_period", "value": max_weeks, "filter": {"years": year}}
        )
        return self

    def min_contiguity_in_year(self, min_contiguity, year: str):
        self._constraints.append(
            {
                "type": "min_contiguity_in_period",
                "value": min_contiguity,
                "filter": {"years": year},
            }
        )
        return self

    def max_contiguity_in_year(self, max_contiguity, year: str):
        self._constraints.append(
            {
                "type": "max_contiguity_in_period",
                "value": max_contiguity,
                "filter": {"years": year},
            }
        )
        return self

    def after_prerequisite(self, prerequisite: str, weeks_completed: int):
        self._constraints.append(
            {
                "type": "prerequisite",
                "value": {prerequisite: weeks_completed},
                "filter": None,
            },
        )
        return self

    def never_broken_up_in_year(self, year: str):
        self._constraints.append(
            {
                "type": "never_broken_up_in_year",
                "value": 1,
                "filter": {"years": year},
            },
        )
        return self

    def exclude_weeks_this_year(self, weeks: List[int]):
        self._constraints.append(
            {
                "type": "exclude_weeks",
                "value": 0,
                "filter": {"weeks": weeks},
            },
        )
        return self

    def get_constraints(self) -> List[Dict[str, Any]]:
        """Get all constraints for this requirement"""
        return self._constraints


class RequirementBuilder:

    def __init__(self):
        self.requirements: Dict[str, RequirementRule] = {}

    def add_requirement(self, name: str, fulfilled_by: List[str]) -> RequirementRule:
        rule = RequirementRule(name=name, fulfilled_by=fulfilled_by)
        self.requirements[name] = rule
        return rule

    def generate_requirements_df(self) -> pl.DataFrame:

        requirements_data = []
        constraints_data = []

        for req_name, req in self.requirements.items():
            # Requirements DataFrame
            requirements_data.append(
                {
                    "name": req.name,
                },
            )

        completed_requirements_df = pl.DataFrame(requirements_data)

        return completed_requirements_df

    def generate_constraints_df(self) -> pl.DataFrame:

        requirements_data = []
        constraints_data = []

        for req_name, req in self.requirements.items():
            # Constraints DataFrame
            for i, constraint in enumerate(req.get_constraints()):
                constraints_data.append(
                    {
                        "requirement_name": req.name,
                        "constraint_id": f"{req_name}_constraint_{i}",
                        "constraint_type": constraint["type"],
                        "constraint_value": constraint["value"],
                        "period_filter": constraint["filter"],
                    },
                )
        completed_constraints_df = pl.DataFrame(constraints_data)

        return completed_constraints_df


if __name__ == "__main__":
    import yaml
    from data_io import dump_polars_df_to_yaml

    builder = RequirementBuilder()

    (
        builder.add_requirement(
            name="HS Rounding Senior",
            fulfilled_by=["HS Orange Senior", "HS Green Senior"],
        )
        .min_weeks_in_year(2, "R2")
        .min_weeks_in_year(8, "R3")
        .min_contiguity_in_year(2, year="R2")
        .after_prerequisite("HS Rounding Intern", 8)
        .never_broken_up_in_year("R2")
        .exclude_weeks_this_year([1])
    )

    ic(builder.requirements)

    print(yaml.dump((builder.requirements)))

    print(dump_polars_df_to_yaml(builder.generate_constraints_df()))
