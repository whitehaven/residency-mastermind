import pandas as pd


def generate_weekly_mondays_with_index_df(
    start_date: str | pd.Timestamp, end_date: str | pd.Timestamp
) -> pd.DataFrame:
    if isinstance(start_date, str) or isinstance(end_date, str):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    weekly_mondays = pd.date_range(start=start_date, end=end_date, freq="W-MON")
    return pd.DataFrame({"date": weekly_mondays})


def convert_date_to_academic_yr_and_wk(date: str | pd.Timestamp,
                                       academic_year_date_ranges=None) -> tuple[str, int]:
    assert isinstance(date, str) or isinstance(date, pd.Timestamp), "bad input type"

    if academic_year_date_ranges is None:
        # my best guess based on schedule spreadsheet, TODO confirm with admin
        academic_year_date_ranges = pd.DataFrame.from_dict({'academic_year': {0: '2025-2026', 1: '2026-2027'},
                                                            'academic_year_integer': {0: 2026, 1: 2027},
                                                            'first_day': {0: pd.Timestamp('2025-06-23 00:00:00'),
                                                                          1: pd.Timestamp('2026-06-22 00:00:00')},
                                                            'last_day': {0: pd.Timestamp('2026-06-21 00:00:00'),
                                                                         1: pd.Timestamp('2027-06-21 00:00:00')}})

    if isinstance(date, pd.Timestamp):
        this_date = date
    else:
        this_date = pd.to_datetime(date)

    academic_year_match = academic_year_date_ranges.query("first_day <= @this_date <= last_day")
    assert len(academic_year_match) == 1, "no or overlapping year returns - check data integrity"

    academic_year = academic_year_match.academic_year.iloc[0]
    assert isinstance(academic_year, str)

    td_since_this_date = (this_date - academic_year_match.first_day.iloc[0])
    week_n = td_since_this_date.days // 7 + 1
    assert 0 < week_n <= 53, "week_n returns out of range"

    return academic_year, week_n


if __name__ == "__main__":
    mondays = generate_weekly_mondays_with_index_df("2025-01-01", "2025-12-31")
    print(mondays)
