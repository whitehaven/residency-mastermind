from dataclasses import dataclass, field
from typing import Any


@dataclass
class RequirementRule:
    name: str
    fulfilled_by: list[str]
    _constraints: list[dict[str, Any]] = field(default_factory=list)

    def min_weeks_over_resident_years(self, min_weeks: int, resident_years: list[str]):
        self._constraints.append(
            {
                "type": "min_by_period",
                "weeks": min_weeks,
                "resident_years": resident_years,
            }
        )
        return self

    def max_weeks_over_resident_years(self, max_weeks: int, resident_years: list[str]):
        self._constraints.append(
            {
                "type": "max_by_period",
                "weeks": max_weeks,
                "resident_years": resident_years,
            }
        )
        return self

    def range_weeks_over_resident_years(
        self, min_weeks: int, max_weeks: int, resident_years: list[str]
    ):
        return self.min_weeks_over_resident_years(
            min_weeks=min_weeks, resident_years=resident_years
        ).max_weeks_over_resident_years(
            max_weeks=max_weeks, resident_years=resident_years
        )

    def exact_weeks_over_resident_years(
        self, exact_weeks: int, resident_years: list[str]
    ):
        self._constraints.append(
            {
                "type": "exact_by_period",
                "weeks": exact_weeks,
                "resident_years": resident_years,
            }
        )
        return self

    def min_contiguity_over_resident_years(
        self, min_contiguity: int, resident_years: list[str]
    ):
        self._constraints.append(
            {
                "type": "min_contiguity_in_period",
                "weeks": min_contiguity,
                "resident_years": resident_years,
            }
        )
        return self

    def max_contiguity_over_resident_years(
        self, max_contiguity: int, resident_years: list[str]
    ):
        self._constraints.append(
            {
                "type": "max_contiguity_in_period",
                "weeks": max_contiguity,
                "resident_years": resident_years,
            }
        )
        return self

    def after_prerequisite(self, prerequisite: str, weeks_required: int):
        self._constraints.append(
            {
                "type": "prerequisite",
                "prerequisite": prerequisite,
                "weeks_required": weeks_required,
            },
        )
        return self

    def exclude_weeks_for_resident_years(
        self, weeks: list[int], resident_years: list[str]
    ):
        """
        Note DOES NOT filter by a resident year - excludes use for purposes of year being solved

        Returns:

        """
        self._constraints.append(
            {
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
        for rule_name, rule_body in self.requirements.items():
            accumulated_constraints.update(
                {
                    rule_name: {
                        "constraints": rule_body.get_constraints(),
                        "fulfilled_by": rule_body.fulfilled_by,
                    }
                }
            )
        return accumulated_constraints


def generate_builder_with_current_requirements() -> RequirementBuilder:
    builder = RequirementBuilder()

    (
        builder.add_requirement(
            name="HS Rounding Senior",
            fulfilled_by=["Orange HS Senior", "Green HS Senior"],
        )
        .min_weeks_over_resident_years(2, ["R2"])
        .max_weeks_over_resident_years(4, ["R2"])
        .exact_weeks_over_resident_years(8, ["R3"])
        .min_contiguity_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(4, ["R3"])
        .min_weeks_over_resident_years(2, ["R3"])
        .after_prerequisite("HS Admitting Senior", 2)
    )

    (
        builder.add_requirement(
            name="HS Admitting Senior", fulfilled_by=["Purple HS Senior"]
        )
        .min_weeks_over_resident_years(5, ["R2"])
        .max_weeks_over_resident_years(6, ["R2"])
        .max_contiguity_over_resident_years(1, ["R2", "R3"])
    )

    (
        builder.add_requirement(
            name="ICU Senior", fulfilled_by=["SHMC ICU Senior"]
        ).min_weeks_over_resident_years(4, ["R2"])
    )
    (
        builder.add_requirement(
            name="Systems of Medicine", fulfilled_by=["Systems of Medicine"]
        )
        .min_weeks_over_resident_years(2, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
    )

    (
        builder.add_requirement(name="Elective", fulfilled_by=["Elective"])
        .min_weeks_over_resident_years(20, ["R2"])
        .max_weeks_over_resident_years(30, ["R2"])
    )

    (
        builder.add_requirement(
            name="Ethics", fulfilled_by=["Ethics"]
        ).exact_weeks_over_resident_years(1, ["R2", "R3"])
    )

    (
        builder.add_requirement(name="Ambulatory Senior", fulfilled_by=["STHC Senior"])
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(2, ["R2"])
        .min_weeks_over_resident_years(4, ["R3"])
        .min_contiguity_over_resident_years(2, ["R3"])
    )

    (  # TODO how does early nights backup work? is it R2s?
        builder.add_requirement(
            name="SHMC Night Senior",
            fulfilled_by=["SHMC Night Senior", "SHMC Backup Night R3"],
        )
        .min_weeks_over_resident_years(4, ["R2"])
        .min_contiguity_over_resident_years(4, ["R2"])
        .min_weeks_over_resident_years(1, ["R3"])
        .max_weeks_over_resident_years(2, ["R3"])
        # .never_broken_up_in_year("R3")
    )

    (
        builder.add_requirement(name="Vacation", fulfilled_by=["Vacation"])
        .exact_weeks_over_resident_years(4, ["R2"])
        .exact_weeks_over_resident_years(3, ["R3"])
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
    import box

    current_builder = generate_builder_with_current_requirements()
    builder_box = box.Box(current_builder.accumulate_constraints_by_rule())
    builder_box.to_yaml("requirements.yaml")
