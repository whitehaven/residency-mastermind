import pandas as pd


def generate_weekly_mondays_with_index_df(
    start_date: str | pd.Timestamp, end_date: str | pd.Timestamp
) -> pd.DataFrame:
    if isinstance(start_date, str) or isinstance(end_date, str):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    weekly_mondays = pd.date_range(start=start_date, end=end_date, freq="W-MON")
    return pd.DataFrame({"date": weekly_mondays})


if __name__ == "__main__":
    mondays = generate_weekly_mondays_with_index_df("2025-01-01", "2025-12-31")
    print(mondays)
