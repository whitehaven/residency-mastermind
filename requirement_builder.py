import json
from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class RequirementRule:
    name: str
    fulfilled_by: list[str]
    _constraints: list[dict[str, Any]] = field(default_factory=list)

    def min_weeks_over_resident_years(
        self, min_weeks: int, resident_years: str | list[str]
    ):
        self._constraints.append(
            {
                "fulfilled_by": self.fulfilled_by,
                "type": "min_by_period",
                "weeks": min_weeks,
                "resident_years": resident_years,
            }
        )
        return self

    def max_weeks_over_resident_years(
        self, max_weeks: int, resident_years: str | list[str]
    ):
        self._constraints.append(
            {
                "fulfilled_by": self.fulfilled_by,
                "type": "max_by_period",
                "weeks": max_weeks,
                "resident_years": resident_years,
            }
        )
        return self

    def range_weeks_over_resident_years(
        self, min_weeks: int, max_weeks: int, resident_years: str | list[str]
    ):
        return self.min_weeks_over_resident_years(
            min_weeks=min_weeks, resident_years=resident_years
        ).max_weeks_over_resident_years(
            max_weeks=max_weeks, resident_years=resident_years
        )

    def exact_weeks_over_resident_years(
        self, exact_weeks: int, resident_years: str | list[str]
    ):
        self._constraints.append(
            {
                "fulfilled_by": self.fulfilled_by,
                "type": "exact_by_period",
                "weeks": exact_weeks,
                "resident_years": resident_years,
            }
        )
        return self

    def min_contiguity_over_resident_years(
        self, min_contiguity: int, resident_years: str | list[str]
    ):
        self._constraints.append(
            {
                "fulfilled_by": self.fulfilled_by,
                "type": "min_contiguity",
                "weeks": min_contiguity,
                "resident_years": resident_years,
            }
        )
        return self

    def max_contiguity_over_resident_years(
        self, max_contiguity: int, resident_years: str | list[str]
    ):
        self._constraints.append(
            {
                "fulfilled_by": self.fulfilled_by,
                "type": "max_contiguity_in_period",
                "weeks": max_contiguity,
                "resident_years": resident_years,
            }
        )
        return self

    def after_prerequisite(self, prerequisite: str, weeks_required: int):
        self._constraints.append(
            {
                "fulfilled_by": self.fulfilled_by,
                "type": "prerequisite",
                "prerequisite": prerequisite,
                "weeks_required": weeks_required,
            },
        )
        return self

    def exclude_weeks_for_resident_years(
        self, weeks: list[int], resident_years: str | list[str]
    ):
        """
        Note DOES NOT filter by a resident year - excludes use for purposes of year being solved
        Args:
            resident_years:
            weeks:

        Returns:

        """
        self._constraints.append(
            {
                "fulfilled_by": self.fulfilled_by,
                "type": "exclude_weeks",
                "excluded_weeks": weeks,
                "resident_years": resident_years,
            },
        )
        return self

    def get_constraints(self) -> list[dict[str, Any]]:
        """Get all constraints for this requirement"""
        return self._constraints


class RequirementBuilder:

    def __init__(self):
        self.requirements: dict[str, RequirementRule] = {}

    def add_requirement(self, name: str, fulfilled_by: list[str]) -> RequirementRule:
        rule = RequirementRule(name=name, fulfilled_by=fulfilled_by)
        self.requirements[name] = rule
        return rule

    def accumulate_constraints_by_rule(self) -> dict:
        accumulated_constraints = dict()
        for rule_name, rule_constraints in self.requirements.items():
            accumulated_constraints.update(
                {rule_name: rule_constraints.get_constraints()}
            )
        return accumulated_constraints

    def write_yaml(self, yaml_path: str = "requirements.yaml") -> None:
        with open(yaml_path, "w") as reqs:
            yaml.dump(self.accumulate_constraints_by_rule(), stream=reqs)

    def to_yaml(self) -> str:
        return yaml.dump(self.accumulate_constraints_by_rule())

    def write_json(self, json_path: str = "requirements.json") -> None:
        with open(json_path, "w") as reqs_file:
            json.dump(self.accumulate_constraints_by_rule(), reqs_file)

    def to_json(self) -> str:
        return json.dumps(self.accumulate_constraints_by_rule(), indent=2)


def generate_builder_with_current_requirements() -> RequirementBuilder:
    builder = RequirementBuilder()

    (
        builder.add_requirement(
            name="HS Rounding Senior",
            fulfilled_by=["HS Orange Senior", "HS Green Senior"],
        )
        .min_weeks_over_resident_years(2, "R2")
        .max_weeks_over_resident_years(4, "R2")
        .exact_weeks_over_resident_years(8, "R3")
        .min_contiguity_over_resident_years(2, "R2")
        .min_contiguity_over_resident_years(4, "R3")
        .min_weeks_over_resident_years(2, "R3")
        .after_prerequisite("HS Admitting Senior", 2)
    )

    (
        builder.add_requirement(
            name="HS Admitting Senior", fulfilled_by=["Purple Senior"]
        )
        .min_weeks_over_resident_years(5, "R2")
        .max_weeks_over_resident_years(6, "R2")
        .max_contiguity_over_resident_years(1, ["R2", "R3"])
    )

    (
        builder.add_requirement(
            name="ICU Senior", fulfilled_by=["SHMC ICU Senior"]
        ).min_weeks_over_resident_years(4, "R2")
    )
    (
        builder.add_requirement(
            name="Systems of Medicine", fulfilled_by=["Systems of Medicine"]
        )
        .min_weeks_over_resident_years(2, "R2")
        .min_contiguity_over_resident_years(2, "R2")
    )

    (
        builder.add_requirement(name="Elective", fulfilled_by=["Elective"])
        .min_weeks_over_resident_years(20, "R2")
        .max_weeks_over_resident_years(30, "R2")
    )

    (
        builder.add_requirement(
            name="Ethics", fulfilled_by=["Ethics"]
        ).exact_weeks_over_resident_years(1, ["R2", "R3"])
    )

    (
        builder.add_requirement(name="Ambulatory Senior", fulfilled_by=["STHC Senior"])
        .min_weeks_over_resident_years(4, "R2")
        .min_contiguity_over_resident_years(2, "R2")
        .min_weeks_over_resident_years(4, "R3")
        .min_contiguity_over_resident_years(2, "R3")
    )

    (  # TODO how does early nights backup work? is it R2s?
        builder.add_requirement(
            name="Night Senior", fulfilled_by=["Night Senior", "Backup Night R3"]
        )
        .min_weeks_over_resident_years(4, "R2")
        .min_contiguity_over_resident_years(4, "R2")
        .min_weeks_over_resident_years(1, "R3")
        .max_weeks_over_resident_years(2, "R3")
        # .never_broken_up_in_year("R3")
    )

    (
        builder.add_requirement(name="Vacation", fulfilled_by=["Vacation"])
        .exact_weeks_over_resident_years(4, "R2")
        .exact_weeks_over_resident_years(3, "R3")
        # TODO need to get number that R1s actually get, or would just go on R1 schedule?
    )

    # TODO might be better implemented by rotation?
    # (
    #     current_builder.add_requirement(
    #         name="Backup Night Senior", fulfilled_by=["Backup Night Senior"]
    #     )
    #     .only_include_weeks_this_year([1, 2, 5, 6])
    #     .min_weeks_in_year(0, "R3")
    # )

    return builder


if __name__ == "__main__":
    current_builder = generate_builder_with_current_requirements()
    print(current_builder.to_yaml())
    print(current_builder.to_json())
