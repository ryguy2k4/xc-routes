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
df_tracks.to_parquet("data/intermediate/track_info_parsed.parquet")

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

    # start / end points
    start_point = gdf.iloc[0]["geometry"]
    end_point = gdf.iloc[-1]["geometry"]

    # start / end times
    start_datetime = gdf["datetime"].min()
    end_datetime = gdf["datetime"].max()

    # elapsed time / duration
    gdf["elapsed_time"] = gdf["datetime"].diff().cumsum()
    gdf["elapsed_time"] = gdf["elapsed_time"].fillna(timedelta(seconds=0))
    total_duration = gdf["elapsed_time"].max()

    # elapsed distance / total distance
    gdf["elapsed_distance (mi)"] = (gdf.to_crs(gdf.estimate_utm_crs())["geometry"].distance(gdf.to_crs(gdf.estimate_utm_crs())["geometry"].shift()).cumsum() / 1609)
    gdf["elapsed_distance (mi)"] = gdf["elapsed_distance (mi)"].fillna(0)
    total_distance = gdf["elapsed_distance (mi)"].max()

    # pace
    gdf["pace (min/mi)"] = (gdf["elapsed_time"].dt.total_seconds() / 60).diff(10) / gdf["elapsed_distance (mi)"].diff(10)
    gdf["pace (min/mi)"] = gdf["pace (min/mi)"].bfill()
    average_pace = gdf.loc[gdf["pace (min/mi)"] < 10, "pace (min/mi)"].mean()

    # elevation
    total_elevation_change = np.abs(gdf["elevation"].diff()).sum()

    # track line
    def amend_track_pauses(gdf_track_points):
        # get diffs column to detect outliers which indicate a pause
        gdf_utm = gdf_track_points.to_crs(gdf_track_points.estimate_utm_crs())
        diffs = gdf_utm["geometry"].distance(gdf_utm["geometry"].shift())[1::]
        # calculate outlier threshold
        t = np.mean(diffs) + 10*np.std(diffs)
        # get outlier indices
        split_idx = diffs[diffs > t].index
        # split linestring at pauses
        segments = []
        prev_idx = 0
        for idx in split_idx:
            if (idx - prev_idx) < 2:
                continue
            segments.append(gdf.iloc[prev_idx:idx]['geometry'])
            prev_idx = idx
        # always add last segment
        last_segment = gdf.iloc[prev_idx::]['geometry']
        if len(last_segment) > 1:
            segments.append(last_segment)
        # recombine as multilinestring
        return shapely.MultiLineString([shapely.LineString(c) for c in segments])
    track_line = amend_track_pauses(gdf)

    return {
        "start_point": start_point,
        "end_point": end_point,
        "track_line": track_line,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "total_duration": total_duration,
        "total_distance (mi)": total_distance,
        "average_pace (min/mi)": average_pace,
        "total_elevation_change (m)": total_elevation_change,
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
        "year",
        "season",
        "total_duration",
        "total_distance (mi)",
        "average_pace (min/mi)",
        "total_elevation_change (m)",
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