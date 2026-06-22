from datetime import datetime
import pandas as pd

MIN_DATE = datetime(2019, 6, 10)
MAX_DATE = datetime(2023, 5, 16)
seasons = pd.DataFrame(
    [
        {
            "year": "Freshman",
            "season": "Summer Training",
            "start_date": datetime(2019, 6, 10),
            "end_date": datetime(2019, 8, 11),
        },
        {
            "year": "Freshman",
            "season": "XC Season",
            "start_date": datetime(2019, 8, 12),
            "end_date": datetime(2019, 11, 7),
        },
        {
            "year": "Freshman",
            "season": "Winter Training",
            "start_date": datetime(2019, 11, 23),
            "end_date": datetime(2020, 1, 26),
        },
        {
            "year": "Freshman",
            "season": "Track Season",
            "start_date": datetime(2020, 1, 27),
            "end_date": datetime(2020, 5, 1),
        },
        {
            "year": "Sophomore",
            "season": "Summer Training",
            "start_date": datetime(2020, 5, 26),
            "end_date": datetime(2020, 8, 9),
        },
        {
            "year": "Sophomore",
            "season": "XC Season",
            "start_date": datetime(2020, 8, 10),
            "end_date": datetime(2020, 10, 18),
        },
        {
            "year": "Sophomore",
            "season": "Winter Training",
            "start_date": datetime(2020, 11, 9),
            "end_date": datetime(2021, 4, 4),
        },
        {
            "year": "Sophomore",
            "season": "Track Season",
            "start_date": datetime(2021, 4, 5),
            "end_date": datetime(2021, 6, 9),
        },
        {
            "year": "Junior",
            "season": "Summer Training",
            "start_date": datetime(2021, 6, 28),
            "end_date": datetime(2021, 8, 8),
        },
        {
            "year": "Junior",
            "season": "XC Season",
            "start_date": datetime(2021, 8, 9),
            "end_date": datetime(2021, 10, 24),
        },
        {
            "year": "Junior",
            "season": "Winter Training",
            "start_date": datetime(2021, 11, 22),
            "end_date": datetime(2022, 1, 30),
        },
        {
            "year": "Junior",
            "season": "Track Season",
            "start_date": datetime(2022, 1, 31),
            "end_date": datetime(2022, 4, 27),
        },
        {
            "year": "Senior",
            "season": "Summer Training",
            "start_date": datetime(2022, 6, 13),
            "end_date": datetime(2022, 8, 7),
        },
        {
            "year": "Senior",
            "season": "XC Season",
            "start_date": datetime(2022, 8, 8),
            "end_date": datetime(2022, 11, 5),
        },
        {
            "year": "Senior",
            "season": "Winter Training",
            "start_date": datetime(2022, 12, 1),
            "end_date": datetime(2023, 1, 29),
        },
        {
            "year": "Senior",
            "season": "Track Season",
            "start_date": datetime(2023, 1, 30),
            "end_date": datetime(2023, 5, 16),
        },
    ]
)


def bucket_date(date):
    for i, row in seasons.iterrows():
        if (date >= row["start_date"]) & (date <= row["end_date"]):
            return row["year"], row["season"]
    return (None, None)
