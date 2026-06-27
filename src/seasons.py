from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

MIN_DATE = datetime(2019, 6, 10, tzinfo=ZoneInfo("America/Chicago"))
MAX_DATE = datetime(2023, 5, 16, tzinfo=ZoneInfo("America/Chicago"))
seasons = pd.DataFrame(
    [
        {
            "year": "Freshman",
            "season": "Summer Training",
            "start_date": datetime(2019, 6, 10, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2019, 8, 12, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Freshman",
            "season": "XC Season",
            "start_date": datetime(2019, 8, 12, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2019, 11, 8, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Freshman",
            "season": "Winter Training",
            "start_date": datetime(2019, 11, 8, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2020, 1, 27, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Freshman",
            "season": "Track Season",
            "start_date": datetime(2020, 1, 27, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2020, 5, 2, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Sophomore",
            "season": "Summer Training",
            "start_date": datetime(2020, 5, 2, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2020, 8, 10, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Sophomore",
            "season": "XC Season",
            "start_date": datetime(2020, 8, 10, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2020, 10, 19, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Sophomore",
            "season": "Winter Training",
            "start_date": datetime(2020, 10, 19, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2021, 4, 5, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Sophomore",
            "season": "Track Season",
            "start_date": datetime(2021, 4, 5, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2021, 6, 10, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Junior",
            "season": "Summer Training",
            "start_date": datetime(2021, 6, 10, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2021, 8, 9, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Junior",
            "season": "XC Season",
            "start_date": datetime(2021, 8, 9, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2021, 10, 25, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Junior",
            "season": "Winter Training",
            "start_date": datetime(2021, 10, 25, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2022, 1, 31, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Junior",
            "season": "Track Season",
            "start_date": datetime(2022, 1, 31, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2022, 4, 28, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Senior",
            "season": "Summer Training",
            "start_date": datetime(2022, 4, 28, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2022, 8, 8, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Senior",
            "season": "XC Season",
            "start_date": datetime(2022, 8, 8, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2022, 11, 6, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Senior",
            "season": "Winter Training",
            "start_date": datetime(2022, 11, 6, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2023, 1, 30, tzinfo=ZoneInfo("America/Chicago")),
        },
        {
            "year": "Senior",
            "season": "Track Season",
            "start_date": datetime(2023, 1, 30, tzinfo=ZoneInfo("America/Chicago")),
            "end_date": datetime(2023, 5, 16, tzinfo=ZoneInfo("America/Chicago")),
        },
    ]
)


def bucket_date(date):
    for i, row in seasons.iterrows():
        if (date >= row["start_date"]) & (date < row["end_date"]):
            return row["year"], row["season"]
    print(f"No Match for {date}")
    return (None, None)
