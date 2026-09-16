import cpmpy as cp
import polars as pl

import config


def accumulate_req_constraints(
    workers_with_reqsets: pl.DataFrame,
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generates and accumulates all constraints which pertain to supplied workers, rotations, and weeks.

    :param workers_with_reqsets: workers df with assigned reqs columns as ["req_set"]
    :param rotations:
    :param weeks:
    :param scheduled:
    :return:
    """

    cumu_constraints = []

    for worker in workers_with_reqsets.iter_rows(named=True):
        for req_name, req_body in worker["req_set"].items():
            for constraint in req_body["constraints"]:
                match constraint:
                    case "max_weeks":
                        cumu_constraints.extend(
                            generate_max_weeks_req_constraints(
                                scheduled.filter(pl.col("name") == worker["name"]),
                                fulfilling_rotations=req_body["fulfilled_by"],
                                max_weeks=req_body["constraints"]["max_weeks"],
                            )
                        )
                    case "min_weeks":
                        cumu_constraints.extend(
                            generate_min_weeks_req_constraints(
                                scheduled.filter(pl.col("name") == worker["name"]),
                                fulfilling_rotations=req_body["fulfilled_by"],
                                min_weeks=req_body["constraints"]["min_weeks"],
                            )
                        )
                    case "min_contiguity":
                        cumu_constraints.extend(
                            generate_min_contiguity_req_constraints(
                                scheduled.filter(pl.col("name") == worker["name"]),
                                affected_rotations=req_body["fulfilled_by"],
                                min_contiguity=req_body["constraints"][
                                    "min_contiguity"
                                ],
                            )
                        )
                    case "max_contiguity":
                        cumu_constraints.extend(
                            generate_max_contiguity_req_constraints(
                                scheduled.filter(pl.col("name") == worker["name"]),
                                affected_rotations=req_body["fulfilled_by"],
                                max_contiguity=req_body["constraints"][
                                    "max_contiguity"
                                ],
                            )
                        )
                    case "prerequisite":
                        cumu_constraints.extend(
                            generate_prerequisite_constraints(
                                scheduled.filter(pl.col("name") == worker["name"]),
                                weeks=weeks,
                                affected_rotations=req_body["fulfilled_by"],
                                rots_meeting_prereqs=req_body["constraints"][
                                    "prerequisite"
                                ]["rots_meeting_prereqs"],
                                prereq_weeks=req_body["constraints"]["prerequisite"][
                                    "weeks"
                                ],
                            )
                        )
                    case "must_be_succeeded_by":
                        cumu_constraints.extend(
                            generate_must_be_succeeded_by_constraints(
                                scheduled.filter(pl.col("name") == worker["name"]),
                                weeks=weeks,
                                rots_that_must_be_succeeded=req_body["fulfilled_by"],
                                rots_that_must_succeed=req_body["constraints"][
                                    "must_be_succeeded_by"
                                ],
                            )
                        )
                    case _:
                        raise NotImplementedError(
                            f"{constraint=} not a known constraint"
                        )

    return cumu_constraints


def accumulate_rotation_constraints(
    workers: pl.DataFrame,  # TODO: not clear if needs to pass this since it applies to everyone universally
    rotations: dict[str, dict],
    weeks: pl.DataFrame,
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generate rotation-specific constraints which are applied to all workers. These represent nonfungible locations.

    :param workers: pl.DataFrame with workers assigned. For convenience, can include reqs columns as ["req_set"] but not needed here.
    :param rotations:
    :param weeks:
    :param scheduled:
    :return:
    """
    cumu_constraints = []
    for rot_name, rot_body in rotations.items():
        for constraint_name, constraint_value in rot_body.items():
            match constraint_name:
                case "max_workers_assigned":
                    cumu_constraints.extend(
                        generate_rot_max_workers_constraints(
                            scheduled, rot_name, constraint_value
                        )
                    )
                case "min_workers_assigned":
                    cumu_constraints.extend(
                        generate_rot_min_workers_constraints(
                            scheduled, rot_name, constraint_value
                        )
                    )
                case _:
                    raise NotImplementedError(
                        f"{constraint_name=} not a known constraint"
                    )

    return cumu_constraints


def generate_every_worker_is_somewhere_constraints(
    scheduled: pl.DataFrame,
) -> list[cp.core.Comparison]:
    """
    Generate constraints that require each worker is on exactly one rotation each week.


    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :return:
    """
    cumu_constraints = []
    for worker in scheduled.partition_by("name"):
        for week in worker.partition_by("monday_date"):
            all_rot_vars_this_worker_this_week = week[
                config.CPMPY_VARIABLE_COLUMN
            ].to_list()
            cumu_constraints.append(cp.sum(all_rot_vars_this_worker_this_week) == 1)

    return cumu_constraints


def generate_rot_max_workers_constraints(
    scheduled: pl.DataFrame,
    rotation: str,
    max_workers: int,
) -> list[cp.core.Comparison]:
    """
    For each week in `weeks`, require that no more than `max_workers_assigned`
    workers are scheduled to `rotation`. i.e. sum of that week's BoolVars for this
    rotation (one per worker) is <= `max_workers_assigned`.

    2026-09-09 Note: Polars cannot `group_by(...).agg(list)` an `Object`-dtype column (the BoolVars), so each week's
    group is instead materialized with `partition_by("week")` and the Object column unwrapped with `.to_list()` to
    hand cpmpy a plain list to sum. This was done in prior version (and used in `residency-mastermind` v0.9 and
    prior) but now deprecated, reflecting intention of group_by to be for calculation purposes only.

    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param rotation:
    :param max_workers:
    :return:
    """
    cumu_constraints = []

    # TODO: could this be generalized?

    scheduled_vars_this_rotation = scheduled.filter(pl.col("rotation") == rotation)

    for week_group in scheduled_vars_this_rotation.partition_by("week"):
        week_vars = week_group[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(week_vars) <= max_workers)

    return cumu_constraints


def generate_rot_min_workers_constraints(
    scheduled: pl.DataFrame, rotation: str, min_workers: int
) -> list[cp.core.Comparison]:
    """
    For each week in `weeks`, require that no fewer than `min`
    workers are scheduled to `rotation`. i.e. sum of that week's BoolVars for this
    rotation (one per worker) is <= `max_workers_assigned`.

    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param rotation:
    :param min_workers:
    :return:
    """
    cumu_constraints = []

    scheduled_vars_this_rotation = scheduled.filter(pl.col("rotation") == rotation)

    for week_group in scheduled_vars_this_rotation.partition_by("week"):
        week_vars = week_group[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(week_vars) >= min_workers)

    return cumu_constraints


def generate_min_weeks_req_constraints(
    scheduled: pl.DataFrame, fulfilling_rotations: list[str], min_weeks: int
) -> list[cp.core.Comparison]:
    """
    For each worker included, require that no fewer than `min` weeks are scheduled to `fulfilling rotations`.

    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param fulfilling_rotations:
    :param min_weeks:
    :return:
    """
    cumu_constraints = []

    scheduled_fulfilling_rotations = scheduled.filter(
        pl.col("rotation").is_in(fulfilling_rotations)
    )

    for worker in scheduled_fulfilling_rotations.partition_by("name"):
        this_workers_vars = worker[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(this_workers_vars) >= min_weeks)

    return cumu_constraints


def generate_max_weeks_req_constraints(
    scheduled: pl.DataFrame, fulfilling_rotations: list[str], max_weeks: int
) -> list[cp.core.Comparison]:
    """
    For each worker included, require that no more than `max` weeks are scheduled to `fulfilling rotations`.

    :param scheduled: *pre-filtered* scheduled df containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param fulfilling_rotations:
    :param max_weeks:
    :return:
    """
    cumu_constraints = []

    scheduled_fulfilling_rotations = scheduled.filter(
        pl.col("rotation").is_in(fulfilling_rotations)
    )

    for worker in scheduled_fulfilling_rotations.partition_by("name"):
        this_workers_vars = worker[config.CPMPY_VARIABLE_COLUMN].to_list()
        cumu_constraints.append(cp.sum(this_workers_vars) <= max_weeks)

    return cumu_constraints


def generate_min_contiguity_req_constraints(
    scheduled: pl.DataFrame, affected_rotations: list[str], min_contiguity: int
) -> list[cp.core.Comparison]:
    """
    Generate set of constraints that will require scheduled time on a rotation is always greater than or equal to `min_contiguity`.

    For example, if a requirement is that 4 weeks are spent on HS Rounding Senior rotations, any week that is scheduled must be part of a segment of 4 weeks.

    Encoding: for each rotation, look at that worker's per-rotation vars `x[w]` in chronological order. Every maximal
    run of 1s must have length >= `min_contiguity`. Enforced in two parts per possible run start `w`:
      * if the run starts at `w` (x[w] and not x[w-1]) and `w + min_contiguity - 1` fits in the schedule, the next
        `min_contiguity - 1` weeks must also be 1;
      * no run may start in the last `min_contiguity - 1` weeks, since it could never reach the required length.

    :param scheduled: *pre-filtered* scheduled df (single worker) containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param affected_rotations:
    :param min_contiguity:
    :return:
    """
    cumu_constraints = []

    if min_contiguity <= 1:
        return cumu_constraints

    for rotation in affected_rotations:
        scheduled_this_rotation = scheduled.filter(pl.col("rotation") == rotation).sort(
            by="monday_date"
        )
        week_vars = scheduled_this_rotation[config.CPMPY_VARIABLE_COLUMN].to_list()
        num_weeks = len(week_vars)

        if num_weeks < min_contiguity:
            for var in week_vars:
                cumu_constraints.append(var == 0)
            continue

        for run_start_idx in range(num_weeks - min_contiguity + 1):
            run_starts_here = week_vars[run_start_idx] & (
                ~week_vars[run_start_idx - 1] if run_start_idx > 0 else True
            )
            rest_of_run_vars = week_vars[
                run_start_idx + 1 : run_start_idx + min_contiguity
            ]
            cumu_constraints.append(run_starts_here.implies(cp.all(rest_of_run_vars)))

        for run_start_idx in range(num_weeks - min_contiguity + 1, num_weeks):
            cumu_constraints.append(
                ~(week_vars[run_start_idx] & ~week_vars[run_start_idx - 1])
            )

    return cumu_constraints


def generate_max_contiguity_req_constraints(
    scheduled: pl.DataFrame, affected_rotations: list[str], max_contiguity: int
) -> list[cp.core.Comparison]:
    """
    Generate set of constraints that will require scheduled time on a rotation never stays contiguous for more than
    `max_contiguity` weeks in a row.

    For example, if a requirement is that a resident is on ICU Senior at most 2 weeks at a stretch, any week that is
    scheduled must be part of a segment of no more than 2 weeks.

    Encoding: for each rotation, look at that worker's per-rotation vars `x[w]` in chronological order. Every maximal
    run of 1s must have length <= `max_contiguity`. Equivalently, no window of `max_contiguity + 1` consecutive weeks
    may be fully scheduled, i.e. `cp.sum(x[w : w + max_contiguity + 1]) <= max_contiguity` for every window start `w`.

    :param scheduled: *pre-filtered* scheduled df (single worker) containing cpmpy variables at the config.CPMPY_VARIABLE_COLUMN
    :param affected_rotations:
    :param max_contiguity:
    :return:
    """
    cumu_constraints = []

    if max_contiguity < 1:
        raise ValueError(f"{max_contiguity=} must be a positive integer")

    for rotation in affected_rotations:
        scheduled_this_rotation = scheduled.filter(pl.col("rotation") == rotation).sort(
            by="monday_date"
        )
        week_vars = scheduled_this_rotation[config.CPMPY_VARIABLE_COLUMN].to_list()
        num_weeks = len(week_vars)

        if num_weeks <= max_contiguity:
            continue

        for run_start_idx in range(num_weeks - max_contiguity):
            window_vars = week_vars[run_start_idx : run_start_idx + max_contiguity + 1]
            cumu_constraints.append(cp.sum(window_vars) <= max_contiguity)

    return cumu_constraints


def generate_prerequisite_constraints(
    scheduled: pl.DataFrame,
    weeks: pl.DataFrame,
    affected_rotations: list[str],
    rots_meeting_prereqs: list[str],
    prereq_weeks: int,
) -> list[cp.core.Comparison]:
    cumu_constraints = []

    for worker_sched_vars_df in scheduled.partition_by("name"):
        for rotation in affected_rotations:
            for week in weeks.iter_rows(named=True):
                vars_rots_meeting_prereq_before_this_week = worker_sched_vars_df.filter(
                    (pl.col("monday_date") < week["monday_date"])
                    & (pl.col("rotation").is_in(rots_meeting_prereqs))
                )[config.CPMPY_VARIABLE_COLUMN].to_list()

                var_this_week_receiving_prereqs = worker_sched_vars_df.filter(
                    (pl.col("rotation") == rotation)
                    & (pl.col("monday_date") == week["monday_date"])
                )[config.CPMPY_VARIABLE_COLUMN].item()

                cumu_constraints.append(
                    var_this_week_receiving_prereqs.implies(
                        cp.sum(vars_rots_meeting_prereq_before_this_week)
                        >= prereq_weeks
                    )
                )

    return cumu_constraints


def generate_must_be_succeeded_by_constraints(
    scheduled: pl.DataFrame,
    weeks: pl.DataFrame,
    rots_that_must_be_succeeded: list[str],
    rots_that_must_succeed: list[str],
) -> list[cp.core.Comparison]:
    cumu_constraints = []

    for worker_sched_vars_df in scheduled.partition_by("name"):
        for rot_that_must_be_succeeded in rots_that_must_be_succeeded:
            for rot_that_must_succeed in rots_that_must_succeed:
                all_weeks_rot_must_be_succeeded = worker_sched_vars_df.filter(
                    pl.col("rotation") == rot_that_must_be_succeeded
                )[config.CPMPY_VARIABLE_COLUMN].to_list()
                all_weeks_rot_must_succeed = worker_sched_vars_df.filter(
                    pl.col("rotation") == rot_that_must_succeed
                )[config.CPMPY_VARIABLE_COLUMN].to_list()

                for idx, week in enumerate(all_weeks_rot_must_be_succeeded):
                    week.implies(all_weeks_rot_must_succeed[idx + 1])
                    # This would work except that the must_succeed rotation could be one of several.
                    # Doesn't matter in reverse because the worker could only be on one rotation.

            # for all rots_must_be_succeeded - 1
            # s[week n][rot_that_must_be_succeeded] -> s[week n+1][this rot_must_be_succeeded]
