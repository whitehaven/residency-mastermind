from dataclasses import dataclass, field
from typing import Dict, List, Any, Set

import polars as pl
from icecream import ic


@dataclass
class RequirementRule:
    # TODO should just let dicts take sensible forms with common label to differentiate operations. nulls never hurt anyone. could even do just dicts, but being able persist to sqlite easily is attractive.
    name: str
    fulfilled_by: Set[str]
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

    def range_weeks_in_year(self, min_weeks: int, max_weeks: int, year: str):
        return self.min_weeks_in_year(min_weeks=min_weeks, year=year).max_weeks_in_year(
            max_weeks=max_weeks, year=year
        )

    def exact_weeks_in_year(self, exact_weeks: int, year: str):
        self._constraints.append(
            {"type": "exact_by_period", "value": exact_weeks, "filter": {"years": year}}
        )
        return self

    def exact_weeks_total(
        self, exact_weeks: int, years: tuple[str, ...] = ("R2", "R3")
    ):
        self._constraints.append(
            {
                "type": "exact_by_period",
                "value": exact_weeks,
                "filter": {"years": years},
            }
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

    def min_weeks_total(
        self,
        min_weeks: int,
    ):
        self._constraints.append(
            {"type": "min_total", "value": min_weeks, "filter": None}
        )

        return self

    def max_weeks_total(
        self,
        max_weeks: int,
    ):
        self._constraints.append(
            {"type": "max_total", "value": max_weeks, "filter": None}
        )

        return self

    def exactly_n_weeks_total(
        self,
        n_weeks: int,
    ):
        self._constraints.append(
            {"type": "exactly_n_total", "value": n_weeks, "filter": None}
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

    def never_broken_up(self, year: str):
        self._constraints.append(
            {
                "type": "never_broken_up_total",
                "value": 1,
                "filter": {"years": year},
            },
        )
        return self

    def exclude_weeks_this_year(self, weeks: List[int]):
        """
        Note DOES NOT filter by a resident year - excludes use for purposes of year being solved
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

    def only_include_weeks_this_year(self, weeks: List[int]):
        """
        Note DOES NOT filter by a resident year - includes only for purposes of year being solved.

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

    def must_include_weeks_this_year(self, weeks: List[int], years: str):
        """
        Note DOES NOT filter by a resident year - includes only for purposes of year being solved.

        Args:
            weeks:

        Returns:

        """
        self._constraints.append(
            {
                "type": "only_include_weeks",
                "value": 1,
                "filter": {"weeks": weeks, "years": years},
            },
        )
        return self

    def get_constraints(self) -> List[Dict[str, Any]]:
        """Get all constraints for this requirement"""
        return self._constraints


class RequirementBuilder:

    def __init__(self):
        self.requirements: Dict[str, RequirementRule] = {}

    def add_requirement(self, name: str, fulfilled_by: Set[str]) -> RequirementRule:
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
    builder = RequirementBuilder()

    (
        builder.add_requirement(
            name="HS Rounding Senior",
            fulfilled_by={"HS Orange Senior", "HS Green Senior"},
        )
        .min_weeks_in_year(2, "R2")
        .max_weeks_in_year(4, "R2")
        .exact_weeks_in_year(8, "R3")
        .min_contiguity_in_year(2, "R2")
        .min_contiguity_in_year(2, "R3")
        .after_prerequisite("HS Admitting Senior", 2)
    )

    (
        builder.add_requirement(
            name="HS Admitting Senior", fulfilled_by={"Purple Senior"}
        )
        .min_weeks_in_year(5, "R2")
        .max_weeks_in_year(6, "R2")
        .max_contiguity_in_year(1, "R2")
    )

    (  # TODO how does early nights backup work? is it R2s?
        builder.add_requirement(
            name="Night Senior", fulfilled_by={"Night Senior", "Backup Night R3"}
        )
        .min_weeks_in_year(4, "R2")
        .never_broken_up_in_year("R2")
        .min_weeks_in_year(1, "R3")
        .max_weeks_in_year(2, "R3")
        .never_broken_up_in_year("R3")
    )

    (
        builder.add_requirement(
            name="ICU Senior", fulfilled_by={"SHMC ICU Senior"}
        ).min_weeks_in_year(4, "R2")
    )

    (
        builder.add_requirement(name="Ambulatory Senior", fulfilled_by={"STHC Senior"})
        .min_weeks_in_year(4, "R2")
        .min_contiguity_in_year(2, "R2")
        .min_weeks_in_year(4, "R3")
        .min_contiguity_in_year(2, "R3")
    )

    (
        builder.add_requirement(name="Vacation", fulfilled_by={"Vacation"})
        .exact_weeks_in_year(4, "R2")
        .exact_weeks_in_year(3, "R3")
        .must_include_weeks_this_year(
            weeks=[51, 52], years="R2"
        )  # TODO need to get number that R1s actually get, or would just go on R1 schedule?
    )

    (
        builder.add_requirement(
            name="Systems of Medicine", fulfilled_by={"Systems of Medicine"}
        )
        .min_weeks_total(2)
        .min_contiguity_in_year(min_contiguity=2, year="R2")
    )

    (
        builder.add_requirement(name="Elective", fulfilled_by={"Elective"})
        .min_weeks_in_year(min_weeks=20, year="R2")
        .max_weeks_in_year(max_weeks=30, year="R2")
    )

    (
        builder.add_requirement(
            name="Ethics", fulfilled_by={"Ethics"}
        ).exact_weeks_total(exact_weeks=1)
    )

    # TODO might be better implemented by rotation?
    # (
    #     builder.add_requirement(
    #         name="Backup Night Senior", fulfilled_by={"Backup Night Senior"}
    #     )
    #     .only_include_weeks_this_year([1, 2, 5, 6])
    #     .min_weeks_in_year(0, "R3")
    # )

    ic(builder.requirements)

    ic(
        builder.generate_constraints_df().with_columns(
            pl.col("period_filter").struct.unnest()
        )
    )

    # print(yaml.dump(builder.requirements))

    # print(dump_polars_df_to_yaml(builder.generate_constraints_df()))
