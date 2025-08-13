import pandas as pd
from icecream import ic


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


def generate_completed_rotation(resident: str, rotation: str, weeks: int) -> pd.DataFrame:
    return pd.DataFrame({"resident": [resident], "rotation": [rotation], "weeks": [weeks]})


if __name__ == "__main__":
    single_test = generate_completed_rotation("John Doe, DO", "HS Orange Senior", 4)
    second_test = generate_completed_rotation("John Doe, DO", "STHC Ambulatory Senior", 2)
    combo = pd.concat([single_test, second_test], ignore_index=True)
    ic(combo)
