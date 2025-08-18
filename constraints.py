import pandas as pd
from ortools.sat.python import cp_model


def negated_bounded_span(superspan, start, length):
    """Filters an isolated sub-sequence of variables assigned to True.

    Extract the span of Boolean variables [start, start + length), negate them,
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
        sequence.append(superspan[start - 1])
    for i in range(length):
        sequence.append(~superspan[start + i])
    # right border (end of superspan or superspan[start + length])
    if start + length < len(superspan):
        sequence.append(superspan[start + length])
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

    for resident_idx, resident in relevant_residents.iterrows():
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
                                for _, relevant_week in weeks_R1_year.iterrows()
                            ],
                        ]
                    ]
                )
                >= eligible_rotation_groupby_category.minimum_weeks_category.max()
            )
    assign_rotation_every_week(model, relevant_residents, scheduled, weeks_R1_year)


def set_im_r1_constraints(
    residents: pd.DataFrame,
    rotations: pd.DataFrame,
    weeks: pd.DataFrame,
    categories: pd.DataFrame,
    model: cp_model.CpModel,
    scheduled: pd.Series,
    starting_academic_year: int,
) -> None:
    relevant_residents = residents.loc[residents.role == "IM-Intern"]
    eligible_rotations_current_year = pd.merge(
        categories[categories.pertinent_role == "IM-Intern"],
        rotations,
        left_on="category_name",
        right_on="category",
        suffixes=("_category", "_rotation"),
    )
    eligible_rotations_R2_year = pd.merge(
        categories[categories.pertinent_role == "IM-Senior"],
        rotations,
        left_on="category_name",
        right_on="category",
        suffixes=("_category", "_rotation"),
    )
    eligible_rotations_R3_year = pd.merge(
        categories[categories.pertinent_role == "IM-Senior"],
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

    eligible_rotations_im_r1 = pd.merge(
        categories[categories.pertinent_role == "IM-Intern"],
        rotations,
        left_on="category_name",
        right_on="category",
        suffixes=("_category", "_rotation"),
    )

    # meet intern requirements year 1
    for resident_idx, resident in relevant_residents.iterrows():
        for (
            _,
            eligible_rotation_groupby_category,
        ) in eligible_rotations_im_r1.groupby(["category"]):
            model.Add(  # must >= min_weeks
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
                                for _, relevant_week in weeks_R1_year.iterrows()
                            ],
                        ]
                    ]
                )
                >= eligible_rotation_groupby_category.minimum_weeks_category.max()
            )
            model.Add(  # must <= max_weeks
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
                                for _, relevant_week in weeks_R1_year.iterrows()
                            ],
                        ]
                    ]
                )
                <= eligible_rotation_groupby_category.maximum_weeks_category.min()
            )

    # meet residency requirements during the three years
    eligible_rotations_im_total = pd.merge(
        categories[categories.pertinent_role.isin(["IM-Intern", "IM-Senior"])],
        rotations,
        left_on="category_name",
        right_on="category",
        suffixes=("_category", "_rotation"),
    )

    for resident_idx, resident in relevant_residents.iterrows():
        for (
            _,
            eligible_rotation_groupby_category,
        ) in eligible_rotations_im_total.groupby(["category"]):
            model.Add(  # must >= min_weeks in a category throughout R2/R3
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
                                for _, relevant_week in weeks_full_program.iterrows()
                            ],
                        ]
                    ]
                )
                >= eligible_rotation_groupby_category.minimum_weeks_category.max()
            )

    # seniors' vacation must be 3 years in one and 3 in the other
    for resident_idx, resident in relevant_residents.iterrows():
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
