from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import geopandas as gpd
import glob
import numpy as np
import shapely
import seasons


# load track file paths
path = "/Users/ryansponzilli/Developer/Python Projects/health-data/data/raw/apple_health/apple_health_export/workout-routes"
df_tracks = pd.DataFrame({"track_file": glob.glob(path + "/*")})

# parse track file dates
df_tracks["track_file_datetime"] = df_tracks["track_file"].apply(
    lambda x: datetime.strptime(
        x.split("/")[-1].removeprefix("route_")
        .removesuffix(".gpx"), "%Y-%m-%d_%I.%M%p")
        .replace(tzinfo=ZoneInfo("America/Chicago")
    )
)
df_tracks["track_file_date"] = df_tracks["track_file_datetime"].dt.date

# filter for tracks within my high school career
df_tracks = (
    df_tracks.loc[(df_tracks["track_file_datetime"] >= seasons.MIN_DATE) & (df_tracks["track_file_datetime"] <= seasons.MAX_DATE)]
    .sort_values("track_file_datetime")
    .reset_index(drop=True)
)

# bucket dates into seasons
df_tracks["year"] = df_tracks["track_file_datetime"].apply(lambda x: seasons.bucket_date(x)[0])
df_tracks["season"] = df_tracks["track_file_datetime"].apply(lambda x: seasons.bucket_date(x)[1])

# match each GPX track to an Apple Health workout entry
workout_data_parsed = pd.read_parquet("data/parsed/workout_data.parquet")
merge_cols = []
for i, row in df_tracks.iterrows():
    closest_match_idx = np.abs(workout_data_parsed['creation_datetime'] - row["track_file_datetime"]).argmin()
    merge_cols.append(workout_data_parsed.iloc[closest_match_idx]["creation_datetime"])
df_tracks["merge_col"] = merge_cols
# merge datasets to obtain the activity type column
df_tracks = df_tracks.merge(workout_data_parsed[["creation_datetime", "workoutActivityType"]], left_on="merge_col", right_on="creation_datetime", suffixes=[None, "_y"])
# exclude all non-running workouts
df_tracks = df_tracks.loc[df_tracks["workoutActivityType"] == "HKWorkoutActivityTypeRunning"].drop(columns=["merge_col", "creation_datetime", "workoutActivityType"]).reset_index(drop=True)
df_tracks.to_parquet("data/intermediate/track_info_merged.parquet")

# extract statistics from gpx files
def extract_track_info(gpx_file):
    # parse file
    gdf = gpd.read_file(gpx_file, layer="track_points")
    gdf = gdf[["time", "ele", "geometry"]]
    gdf["time"] = pd.to_datetime(gdf["time"])
    gdf = gdf.rename(columns={"time": "datetime", "ele": "elevation"})

    # create helper columns
    gdf['dt'] = gdf["datetime"].diff()
    gdf_utm = gdf.to_crs(gdf.estimate_utm_crs())
    gdf["dx"] = gdf_utm["geometry"].distance(gdf_utm["geometry"].shift())

    # split into segments at pause indices
    pause_idx = list(gdf.loc[gdf['dt'] > timedelta(seconds=1)].index)
    gdf['pause_segment'] = None
    segment_idx = ([0] + pause_idx + [len(gdf)])
    for i in range(len(segment_idx) - 1):
        gdf.loc[segment_idx[i]:segment_idx[i+1], 'pause_segment'] = i

    # remove segments less than 10 seconds, since these are mistakes with no meaningful value
    if len(gdf) > 10:
        gdf = gdf.groupby("pause_segment", group_keys=False).filter(lambda x: len(x) > 10)
    else:
        # prevent the entire dataset from being removed and messing things up later
        # should probably filter for total length earlier in this script
        print(f"{gpx_file} has length {len(gdf)}")

    # calculate pace for each pause segment separately
    def calculate_rolling_pace(gdf):
        # use a 10 second rolling window for calculating pace
        gdf["pace (min/mi)"] = (gdf["dt"].cumsum().dt.total_seconds() / 60).diff(10) / (gdf["dx"].cumsum() / 1609).diff(10)
        # backfill nans that resulted from the rolling window
        gdf["pace (min/mi)"] = gdf["pace (min/mi)"].bfill()
        return gdf
    gdf = gdf.groupby('pause_segment').apply(calculate_rolling_pace).reset_index().drop(columns=["level_1"], errors='ignore')


    # start / end points
    start_point = gdf.iloc[0]["geometry"]
    end_point = gdf.iloc[-1]["geometry"]
    # start / end times
    start_datetime = gdf["datetime"].min()
    end_datetime = gdf["datetime"].max()
    # calculate number of pauses, where a pause is defined as dt > 1 second
    num_pauses = len(gdf.loc[gdf['dt'] > timedelta(seconds=1)])
    # calculate the total duration, defined as the time between starting and ending the activity
    total_duration = gdf['dt'].sum()
    # calculate the active duration, defined as the total time minus any pauses
    active_duration = gdf.loc[gdf['dt'] == timedelta(seconds=1), 'dt'].sum()
    # calculate total distance, excluding pauses
    total_distance_miles = gdf.loc[(gdf['dt'] == timedelta(seconds=1)), 'dx'].sum() / 1609
    # calculate average pace, exclude any pace over 10 min/mi since those are not representative of actual running
    average_pace = gdf.loc[gdf["pace (min/mi)"] < 10, "pace (min/mi)"].mean()
    # calculate total ascent, excluding pauses
    total_ascent = gdf.loc[(gdf['dt'] == timedelta(seconds=1)), 'elevation'].diff().loc[gdf['elevation'].diff() > 0].sum()
    # calculate total descent, excluding pauses
    total_descent = gdf.loc[(gdf['dt'] == timedelta(seconds=1)), 'elevation'].diff().loc[gdf['elevation'].diff() < 0].sum()
    # split each pause segment into a LineString within a MultiLineString
    fixed_track_line = shapely.MultiLineString([shapely.LineString(group['geometry']) for _, group in gdf.groupby('pause_segment')])

    return {
        "start_point": start_point,
        "end_point": end_point,
        "num_pauses": num_pauses,
        "track_line": fixed_track_line,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "total_duration": total_duration,
        "active_duration": active_duration,
        "total_distance (mi)": total_distance_miles,
        "average_pace (min/mi)": average_pace,
        "total_ascent (m)": total_ascent,
        "total_descent (m)": total_descent,
    }

# add extracted stats to dataframe
stat_dicts = df_tracks['track_file'].apply(lambda x: extract_track_info(x))
df_tracks = pd.concat([df_tracks, pd.DataFrame(stat_dicts.to_list())], axis=1)

# add indicator column for routes within St. Charles
def in_stc(geom):
    STC_LAT_MIN = 41.866329
    STC_LAT_MAX = 41.951764
    STC_LON_MIN = -88.382261
    STC_LON_MAX = -88.240518
    lon = geom.coords[0][0]
    lat = geom.coords[0][1]

    return (
        (lon >= STC_LON_MIN)
        & (lon <= STC_LON_MAX)
        & (lat >= STC_LAT_MIN)
        & (lat <= STC_LAT_MAX)
    )
df_tracks['in_stc'] = df_tracks['start_point'].apply(lambda x: in_stc(x))

# organize columns
df_tracks = df_tracks[
    [
        "track_file",
        "track_file_datetime",
        "track_file_date",
        "start_datetime",
        "end_datetime",
        "num_pauses",
        "total_duration",
        "active_duration",
        "total_distance (mi)",
        "average_pace (min/mi)",
        "total_ascent (m)",
        "total_descent (m)",
        "year",
        "season",
        "in_stc",
        "start_point",
        "end_point",
        "track_line",
    ]
]

# turn the dataframe into a geodataframe
df_track_info = gpd.GeoDataFrame(df_tracks, geometry="track_line", crs="EPSG:4326")
df_track_info["start_point"] = gpd.GeoSeries(df_track_info["start_point"], crs=df_track_info.crs)
df_track_info["end_point"] = gpd.GeoSeries(df_track_info["end_point"], crs=df_track_info.crs)
df_track_info.to_parquet("data/cleaned/track_info.parquet")