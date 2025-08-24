import cpmpy as cp
import pandas as pd
import polars as pl
from ortools.sat.python import cp_model


def negated_bounded_span(superspan: pd.Series, start: int, length: int) -> list:
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
    # TODO should be mass setter and accept singletons or lists/ranges
    """
    Add a specific constraint to force a value at the slot described by [resident, rotation, week].

    Only receives reference to the main dataframes for error checking.
    """
    assert resident in residents.full_name.values, f"{resident} not in residents"
    assert rotation in rotations.rotation.values, f"{rotation} not in rotations"
    assert week in weeks.monday_date.values, f"{week} not in weeks"

    model.Add(scheduled.loc[resident, rotation, week] == value)


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


def enforce_minimum_contiguity(residents, rotations, model, scheduled, relevant_weeks):
    # MAYBE may make sense to parse by residents just to cut down on variable creation
    rotations_requiring_contiguity = rotations[rotations.minimum_contiguous_weeks > 1]
    for _, rotation in rotations_requiring_contiguity.iterrows():
        for _, resident in residents.iterrows():
            hard_min = rotation.minimum_contiguous_weeks
            sequence = scheduled.loc[
                pd.IndexSlice[
                    resident.full_name,
                    rotation.rotation,
                    [
                        relevant_week.monday_date
                        for _, relevant_week in relevant_weeks.iterrows()
                    ],
                ]
            ]
            for length in range(1, hard_min):
                for start in range(len(sequence) - length + 1):
                    model.AddBoolOr(negated_bounded_span(sequence, start, length))


def force_single_weekly_scheduling(
    residents: pl.DataFrame,
    rotations: pl.DataFrame,
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list:
    """
        Generates constraints to cause residents to be assigned to a single rotation weekly.

        Note the input can be **subset** which will have the logical effect - if there are different requirements for some residents, they can be set individually.

    Args:
        residents: residents subject to constraint
        rotations: residents subject to constraint
        weeks: residents subject to constraint
        scheduled: decision variable dataframe

    Returns:
        list of constraints (pure function - does not add to model; must be added a la model += []
    """

    constraints = []

    for resident_row in residents.iter_rows(named=True):
        for week_row in weeks.iter_rows(named=True):
            vars_subset = scheduled.filter(
                (pl.col("resident") == resident_row["full_name"])
                & (pl.col("week") == week_row["monday_date"])
            )["is_scheduled_cp_var"].to_list()

            if vars_subset:
                constraints.append(cp.sum(vars_subset) == 1)

    return constraints


if __name__ == "__main__":
    pass
