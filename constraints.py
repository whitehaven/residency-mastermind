import pandas as pd
from ortools.sat.python import cp_model


def negated_bounded_span(superspan:pd.Series, start:int, length:int) -> list:
    # TODO this function may not work, needs to be compared carefully to source
    """Filters an isolated sub-sequence of variables assigned to True.

    Extract the span of Boolean variables [start, start + length], negate them,
    and if there is variables to the left/right of this span, surround the span by
    them in non negated form.

    Args:
      superspan: a list of variables to extract the span from.
      start: the start to the span.
      length: the length of the span.

    Returns:
      a list of variables which conjunction will be false if the sub-list is
      assigned to True, and correctly bounded by variables assigned to False,
      or by the start or end of superspan.
    """
    sequence = []
    # left border (start of superspan, or superspan[start - 1])
    if start > 0:
        sequence.append(superspan.iloc[start - 1])
    for i in range(length):
        sequence.append(~superspan.iloc[start + i])
    # right border (end of superspan or superspan[start + length])
    if start + length < len(superspan):
        sequence.append(superspan.iloc[start + length])
    return sequence


def force_value(
    resident: str,
    rotation: str,
    week: str,
    value: bool,
    model: cp_model.CpModel,
    scheduled: pd.Series,
    residents: pd.DataFrame,
    rotations: pd.DataFrame,
    weeks: pd.DataFrame,
) -> None:
    """
    Add a specific constraint to force a value at the slot described by [resident, rotation, week].

    Only receives reference to the main dataframes for error checking.
    """
    assert resident in residents.full_name.values, f"{resident} not in residents"
    assert rotation in rotations.rotation.values, f"{rotation} not in rotations"
    assert week in weeks.monday_date.values, f"{week} not in weeks"

    model.Add(scheduled.loc[resident, rotation, week] == value)


def assign_rotation_every_week(model, relevant_residents, scheduled, weeks_R1_year):
    # on something every week of their year
    for resident_idx, resident in relevant_residents.iterrows():
        for relevant_week_idx, relevant_week in weeks_R1_year.iterrows():
            model.AddExactlyOne(
                scheduled.loc[
                    pd.IndexSlice[resident.full_name, :, relevant_week.monday_date]
                ]
            )


def forbid_ineligible_rotations(
    categories: pd.DataFrame,
    model: cp_model.CpModel,
    relevant_residents: pd.DataFrame,
    allowed_resident_type: str,
    rotations: pd.DataFrame,
    scheduled: pd.Series,
    relevant_weeks: pd.DataFrame,
):
    ineligible_rotations = pd.merge(
        categories[  # categories that don't match role, but also aren't available to other resident_types
            (categories.pertinent_role != allowed_resident_type)
            & (  # essentially set subtraction
                ~categories.category_name.isin(
                    categories[
                        categories.pertinent_role == allowed_resident_type
                    ].category_name
                )
            )
        ],
        rotations,  # roles are controlled through categories, don't need to filter rotations AFAIK
        left_on="category_name",
        right_on="category",
        suffixes=("_category", "_rotation"),
    )

    for resident_idx, resident in relevant_residents.iterrows():
        for _, ineligible_rotation_groupby_category in ineligible_rotations.groupby(
            ["category"]
        ):
            model.Add(
                sum(
                    scheduled.loc[
                        pd.IndexSlice[
                            resident.full_name,
                            [
                                ineligible_rotation
                                for ineligible_rotation in ineligible_rotation_groupby_category.rotation
                            ],
                            [
                                relevant_week.monday_date
                                for _, relevant_week in relevant_weeks.iterrows()
                            ],
                        ]
                    ]
                )
                == 0
            )


def set_requirements_minimum_weeks(
    eligible_rotations, model, relevant_residents, scheduled, relevant_weeks
):
    for _, resident in relevant_residents.iterrows():
        for (
            _,
            eligible_rotation_groupby_category,
        ) in eligible_rotations.groupby(["category"]):
            model.Add(
                sum(
                    scheduled.loc[
                        pd.IndexSlice[
                            resident.full_name,
                            [
                                eligible_rotation
                                for eligible_rotation in eligible_rotation_groupby_category.rotation
                            ],
                            [
                                relevant_week.monday_date
                                for _, relevant_week in relevant_weeks.iterrows()
                            ],
                        ]
                    ]
                )
                >= eligible_rotation_groupby_category.minimum_weeks_category.max()
            )


def set_single_year_resident_constraints(
    resident_type: str,
    residents: pd.DataFrame,
    rotations: pd.DataFrame,
    weeks: pd.DataFrame,
    categories: pd.DataFrame,
    model: cp_model.CpModel,
    scheduled: pd.Series,
    starting_academic_year: int,
) -> None:
    assert resident_type in ["PMR", "TY"], "invalid resident type"

    relevant_residents = residents.loc[residents.role == resident_type]

    eligible_rotations = pd.merge(
        categories[categories.pertinent_role == resident_type],
        rotations,
        left_on="category_name",
        right_on="category",
        suffixes=("_category", "_rotation"),
    )

    weeks_R1_year = weeks.loc[weeks.starting_academic_year == starting_academic_year]

    set_requirements_minimum_weeks(
        eligible_rotations, model, relevant_residents, scheduled, weeks_R1_year
    )
    assign_rotation_every_week(model, relevant_residents, scheduled, weeks_R1_year)

    forbid_ineligible_rotations(
        categories,
        model,
        relevant_residents,
        resident_type,
        rotations,
        scheduled,
        weeks_R1_year,
    )


def set_IM_R1_constraints(
    residents: pd.DataFrame,
    rotations: pd.DataFrame,
    weeks: pd.DataFrame,
    categories: pd.DataFrame,
    model: cp_model.CpModel,
    scheduled: pd.Series,
    starting_academic_year: int,
) -> None:
    relevant_residents = residents.loc[residents.role == "IM-Intern"]

    eligible_rotations_R1_year = pd.merge(
        categories[categories.pertinent_role == "IM-Intern"],
        rotations,
        left_on="category_name",
        right_on="category",
        suffixes=("_category", "_rotation"),
    )

    weeks_R1_year = weeks.loc[weeks.starting_academic_year == starting_academic_year]
    weeks_R2_year = weeks.loc[
        weeks.starting_academic_year == starting_academic_year + 1
    ]
    weeks_R3_year = weeks.loc[
        weeks.starting_academic_year == starting_academic_year + 2
    ]
    weeks_full_program = weeks

    # meet intern requirements year 1
    set_requirements_minimum_weeks(
        eligible_rotations_R1_year, model, relevant_residents, scheduled, weeks_R1_year
    )

    forbid_ineligible_rotations(
        categories,
        model,
        relevant_residents,
        "IM-Intern",
        rotations,
        scheduled,
        relevant_weeks=weeks_R1_year,  # for only intern year
    )

    # meet senior-level residency requirements during the three years
    # presumes intern requirements all met
    eligible_rotations_IM_total = pd.merge(
        categories[categories.pertinent_role == "IM-Senior"],
        rotations,
        left_on="category_name",
        right_on="category",
        suffixes=("_category", "_rotation"),
    )

    set_requirements_minimum_weeks(
        eligible_rotations_IM_total,
        model,
        relevant_residents,
        scheduled,
        weeks_full_program,
    )

    # seniors' vacation must be 3 years in one and 3 in the other
    for _, resident in relevant_residents.iterrows():
        for weeks_active_year in [weeks_R2_year, weeks_R3_year]:
            model.Add(
                sum(
                    scheduled.loc[
                        pd.IndexSlice[
                            resident.full_name,
                            "Vacation",
                            [
                                week.monday_date
                                for _, week in weeks_active_year.iterrows()
                            ],
                        ]
                    ]
                )
                == 3
            )

    # assigned somewhere every week for year 1
    assign_rotation_every_week(model, relevant_residents, scheduled, weeks_R1_year)


if __name__ == "__main__":
    pass
