import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

import polars as pl


@dataclass
class Rotation:
    name: str
    requirement: Optional[str] = None
    min_residents: Optional[int] = None
    max_residents: Optional[int] = None
    _constraints: List[Dict[str, Any]] = field(default_factory=list)

    def unavailable_weeks_this_year(self, weeks: List[int]):
        self._constraints.append(
            {
                "type": "exclude_weeks",
                "value": 0,
                "filter": {"weeks": weeks},
            },
        )
        return self

    def only_available_weeks_this_year(self, weeks: List[int]):
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
                    "type": "maximum_residents",
                    "value": max_residents,
                    "filter": None,
                },
            )
        else:
            self._constraints.append(
                {
                    "type": "maximum_residents",
                    "value": max_residents,
                    "filter": {"weeks": period},
                },
            )
        return self

    def exactly_n_residents(self, n_residents: int, period: List[int] | str):
        if period == "full":
            self._constraints.append(
                {
                    "type": "exactly_residents",
                    "value": n_residents,
                    "filter": None,
                },
            )
        else:
            self._constraints.append(
                {
                    "type": "exactly_residents",
                    "value": n_residents,
                    "filter": {"weeks": period},
                },
            )
        return self

    def get_constraints(self) -> List[Dict[str, Any]]:
        return self._constraints


class RotationBuilder:
    def __init__(self):
        self.requirements: List[str] = []
        self.rotations: Dict[str, Rotation] = {}

    def add_requirement(self, name: str) -> "RotationBuilder":
        if name not in self.requirements:
            self.requirements.append(name)
        return self

    def add_rotation(
        self,
        name: str,
        requirement: Optional[str] = None,
        min_residents: Optional[int] = None,
        max_residents: Optional[int] = None,
    ) -> Rotation:
        if requirement:
            self.add_requirement(requirement)
        rule = Rotation(
            name=name,
            requirement=requirement,
            min_residents=min_residents,
            max_residents=max_residents,
        )
        self.rotations[name] = rule
        return rule

    def get_rotations_for_requirement(self, requirement: str) -> List[Rotation]:
        return [
            rot for rot in self.rotations.values() if rot.requirement == requirement
        ]

    def to_yaml(self, path: str) -> None:
        data = {
            "requirements": self.requirements,
            "rotations": [
                {
                    "name": rot.name,
                    "requirement": rot.requirement,
                    "min_residents": rot.min_residents,
                    "max_residents": rot.max_residents,
                }
                for rot in self.rotations.values()
            ],
        }
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, path: str) -> "RotationBuilder":
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        builder = cls()
        for req in data.get("requirements", []):
            builder.add_requirement(req)

        for rot_data in data.get("rotations", []):
            builder.add_rotation(
                name=rot_data["name"],
                requirement=rot_data.get("requirement"),
                min_residents=rot_data.get("min_residents"),
                max_residents=rot_data.get("max_residents"),
            )

        return builder

    @classmethod
    def from_csv(cls, path: str) -> "RotationBuilder":
        df = pl.read_csv(path)
        builder = cls()

        for row in df.iter_rows(named=True):
            requirement = row.get("requirement")
            if requirement and requirement != "":
                builder.add_requirement(requirement)

            builder.add_rotation(
                name=row["rotation"],
                requirement=requirement if requirement else None,
                min_residents=row.get("minimum_residents_assigned"),
                max_residents=row.get("maximum_residents_assigned"),
            )

        return builder

    def to_polars(self) -> pl.DataFrame:
        rows = []
        for rot in self.rotations.values():
            rows.append(
                {
                    "rotation": rot.name,
                    "requirement": rot.requirement,
                    "minimum_residents_assigned": rot.min_residents,
                    "maximum_residents_assigned": rot.max_residents,
                }
            )
        return pl.DataFrame(rows)

    def generate_rotations_df(self) -> pl.DataFrame:
        return self.to_polars()

    def generate_constraints_df(self) -> pl.DataFrame:
        constraints_data = []
        for rot_name, rot in self.rotations.items():
            for i, constraint in enumerate(rot.get_constraints()):
                constraints_data.append(
                    {
                        "rotation_name": rot_name,
                        "constraint_id": f"{rot_name}_constraint_{i}",
                        "constraint_type": constraint["type"],
                        "constraint_value": constraint["value"],
                        "period_filter": constraint["filter"],
                    },
                )
        return pl.DataFrame(constraints_data)
