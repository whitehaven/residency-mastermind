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


def force_value(resident: str, rotation: str, week: str, value: bool, model: cp_model.CpModel, scheduled: pd.Series,
                residents: pd.DataFrame,
                rotations: pd.DataFrame, weeks: pd.DataFrame) -> None:
    """
    Add a specific constraint to force a value at the given slot described by [resident, rotation, week].

    Only receives reference to the main dataframes for error checking.
    """
    assert resident in residents.full_name.values, f"{resident} not in residents"
    assert rotation in rotations.rotation.values, f"{rotation} not in rotations"
    assert week in weeks.monday_date.values, f"{week} not in weeks"

    model.Add(scheduled.loc[resident, rotation, week] == value)


def set_single_year_resident_constraints(resident_type: str, residents: pd.DataFrame, rotations: pd.DataFrame,
                                         weeks: pd.DataFrame, categories: pd.DataFrame,
                                         model: cp_model.CpModel, scheduled: pd.Series,
                                         starting_academic_year: int) -> None:
    assert resident_type in ["PMR", "TY"], "invalid resident type"

    eligible_rotations = pd.merge(categories[categories.pertinent_role == resident_type], rotations,
                                  left_on="category_name",
                                  right_on="category",
                                  suffixes=("_category", "_rotation"))

    for resident_idx, resident in residents.loc[residents.role == resident_type].iterrows():
        for (
                eligible_rotation_groupby_category_name,
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
                                for relevant_week_idx, relevant_week in weeks.loc[
                                weeks.starting_academic_year == starting_academic_year
                                ].iterrows()
                            ],
                        ]
                    ]
                )
                >= eligible_rotation_groupby_category.minimum_weeks_category.max()
            )


if __name__ == "__main__":
    pass
