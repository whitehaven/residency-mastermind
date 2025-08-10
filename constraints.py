import itertools as it


def exclude_incompatible_roles(
    model,
    residents,
    rotations_with_categories,
    scheduled,
    weeks,
    role,
    pertinent_allowed_roles
) -> None:
    """
    Exclude incompatible roles for residents based on their role and the rotation categories.
    """
    for resident, rotation in it.product(
        residents.loc[(residents.role == role)].index,
        rotations_with_categories.loc[
            ~((rotations_with_categories.pertinent_role.isin(pertinent_allowed_roles)))
        ].index,
    ):
        for week in weeks.index:
            model.Add(scheduled.loc[(resident, rotation, week)] == False)
