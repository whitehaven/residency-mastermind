from dataclasses import dataclass, field
from typing import Dict, List, Any

import polars as pl
from icecream import ic


@dataclass
class RotationRule:
    name: str
    _constraints: List[Dict[str, Any]] = field(default_factory=list)

    def unavailable_weeks_this_year(self, weeks: List[int]):
        """
        Mark off weeks.
        Args:
            weeks:

        Returns:

        """
        self._constraints.append(
            {
                "type": "exclude_weeks",
                "value": 0,
                "filter": {"weeks": weeks},
            },
        )
        return self

    def only_available_weeks_this_year(self, weeks: List[int]):
        """
        Mark only available weeks. Not for use with unavailable_weeks_this_year()
        Args:
            weeks:

        Returns:

        """
        self._constraints.append(
            {
                "type": "only_include_weeks",
                "value": 1,
                "filter": {"weeks": weeks},
            },
        )
        return self

    def minimum_residents_during_period(
        self, min_residents: int, period: List[int] | str
    ):
        if period == "full":
            self._constraints.append(
                {
                    "type": "minimum_residents",
                    "value": min_residents,
                    "filter": None,
                },
            )
        else:
            self._constraints.append(
                {
                    "type": "minimum_residents",
                    "value": min_residents,
                    "filter": {"weeks": period},
                },
            )
        return self

    def maximum_residents_during_period(
        self, max_residents: int, period: List[int] | str
    ):
        if period == "full":
            self._constraints.append(
                {
                    "type": "minimum_residents",
                    "value": max_residents,
                    "filter": None,
                },
            )
        else:
            self._constraints.append(
                {
                    "type": "minimum_residents",
                    "value": max_residents,
                    "filter": {"weeks": period},
                },
            )
        return self

    def exactly_n_residents(self, n_residents, period: List[int] | str):
        if period == "full":
            self._constraints.append(
                {
                    "type": "minimum_residents",
                    "value": n_residents,
                    "filter": None,
                },
            )
        else:
            self._constraints.append(
                {
                    "type": "minimum_residents",
                    "value": n_residents,
                    "filter": {"weeks": period},
                },
            )

    def get_constraints(self) -> List[Dict[str, Any]]:
        """Get all constraints for this requirement"""
        return self._constraints


class RotationBuilder:

    def __init__(self):
        self.rotations: Dict[str, RotationRule] = {}

    def add_rotation(self, name: str) -> RotationRule:
        rule = RotationRule(name=name)
        self.rotations[name] = rule
        return rule

    def generate_requirements_df(self) -> pl.DataFrame:

        rotations_data = []
        constraints_data = []

        for req_name, req in self.rotations.items():
            # Requirements DataFrame
            rotations_data.append(
                {
                    "name": req.name,
                },
            )

        complete_rotations_df = pl.DataFrame(rotations_data)

        return complete_rotations_df

    def generate_constraints_df(self) -> pl.DataFrame:

        rotations_data = []
        constraints_data = []

        for req_name, req in self.rotations.items():
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

    builder = RotationBuilder()

    (builder.add_rotation("Night Float Backup").exactly_n_residents(1, [1, 5]))

    builder.add_rotation("HS Orange Senior").exactly_n_residents(1, period="full")
    builder.add_rotation("HS Green Senior").exactly_n_residents(1, period="full")
    builder.add_rotation("SHMC ICU Senior").exactly_n_residents(1, period="full")

    ic(builder.rotations)

    ic(builder.generate_constraints_df())

    print(yaml.dump(builder.rotations))
