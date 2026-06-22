from datetime import datetime, timedelta
import pandas as pd
import geopandas as gpd
import glob
import numpy as np
import xml.etree.ElementTree as ET

import seasons


# load track files
path = "/Users/ryansponzilli/Developer/Python Projects/health-data/data/raw/apple_health/apple_health_export/workout-routes"
tracks = glob.glob(path + "/*")
track_datetimes = [datetime.strptime(t.split("/")[-1].removeprefix("route_").removesuffix(".gpx"), "%Y-%m-%d_%I.%M%p") for t in tracks]

# assemble dataframe
df_tracks = pd.DataFrame({"track_file": tracks, "track_file_datetime": track_datetimes})
df_tracks["track_file_date"] = df_tracks["track_file_datetime"].dt.date
df_tracks = (
    df_tracks.loc[(df_tracks["track_file_datetime"] >= seasons.MIN_DATE) & (df_tracks["track_file_datetime"] <= seasons.MAX_DATE)]
    .sort_values("track_file_datetime")
    .reset_index(drop=True)
)


# bucket dates into seasons
df_tracks["year"] = df_tracks["track_file_datetime"].apply(
    lambda x: seasons.bucket_date(x)[0]
)
df_tracks["season"] = df_tracks["track_file_datetime"].apply(
    lambda x: seasons.bucket_date(x)[1]
)
df_tracks = df_tracks.dropna()


# extract statistics from gpx files
def extract_track_info(gpx_file):  
    # parse file
    gdf = gpd.read_file(gpx_file, layer="track_points")
    track_line = gpd.read_file(file, layer="tracks").iloc[0]['geometry']
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

    return (
        start_point,
        end_point,
        track_line,
        start_datetime,
        end_datetime,
        total_duration,
        total_distance,
        average_pace,
        total_elevation_change,
    )


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


df_track_info = df_tracks.copy()
df_track_info["start_point"] = None
df_track_info["end_point"] = None
df_track_info["track_line"] = None
df_track_info["start_datetime"] = None
df_track_info["end_datetime"] = None
df_track_info["total_duration"] = None
df_track_info["total_distance (mi)"] = None
df_track_info["average_pace (min/mi)"] = None
df_track_info["total_elevation_change (m)"] = None
df_track_info["in_stc"] = None

for file in df_tracks["track_file"].to_list():
    start_point, end_point, track_line, start_datetime, end_datetime, total_duration, total_distance, average_pace, total_elevation_change = extract_track_info(file)
    df_track_info.loc[df_track_info["track_file"] == file, "start_point"] = start_point
    df_track_info.loc[df_track_info["track_file"] == file, "end_point"] = end_point
    df_track_info.loc[df_track_info["track_file"] == file, "track_line"] = track_line
    df_track_info.loc[df_track_info["track_file"] == file, "start_datetime"] = start_datetime
    df_track_info.loc[df_track_info["track_file"] == file, "end_datetime"] = end_datetime
    df_track_info.loc[df_track_info["track_file"] == file, "total_duration"] = total_duration
    df_track_info.loc[df_track_info["track_file"] == file, "total_distance (mi)"] = total_distance
    df_track_info.loc[df_track_info["track_file"] == file, "average_pace (min/mi)"] = average_pace
    df_track_info.loc[df_track_info["track_file"] == file, "total_elevation_change (m)"] = total_elevation_change
    df_track_info.loc[df_track_info["track_file"] == file, "in_stc"] = in_stc(start_point)

df_track_info = df_track_info[
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
df_track_info = gpd.GeoDataFrame(df_track_info, geometry="track_line", crs="EPSG:4326")
df_track_info["start_point"] = gpd.GeoSeries(df_track_info["start_point"], crs=df_track_info.crs)
df_track_info["end_point"] = gpd.GeoSeries(df_track_info["end_point"], crs=df_track_info.crs)

### Load APPLE HEALTH WORKOUT XML
filepath = '/Users/ryansponzilli/Developer/Python Projects/health-data/data/raw/apple_health/apple_health_export/export.xml'
# create element tree object
tree = ET.parse(filepath) 
# for every health record, extract the attributes
root = tree.getroot()
workout_list = [x.attrib for x in root.iter('Workout')]
workout_data = pd.DataFrame(workout_list)
workout_data_parsed = workout_data.copy()
# proper type to dates
for col in ['creationDate', 'startDate', 'endDate']:
    workout_data_parsed[col] = pd.to_datetime(workout_data_parsed[col])
workout_data_parsed['duration'] = workout_data_parsed['duration'].astype(float)
# get relevant dates
workout_data_parsed = workout_data_parsed.loc[(workout_data_parsed['startDate'] >= pd.to_datetime(seasons.MIN_DATE, utc=True)) & (workout_data_parsed['startDate'] <= pd.to_datetime(seasons.MAX_DATE, utc=True))]
# get relevant data
workout_data_parsed = workout_data_parsed.loc[workout_data_parsed['sourceName'] != "Strava"]
workout_data_parsed = workout_data_parsed[["workoutActivityType", "creationDate", "startDate", "endDate", "duration", "durationUnit"]].rename(columns={"creationDate": "creation_datetime", "startDate": "start_datetime", "endDate": "end_datetime"})
workout_data_parsed = workout_data_parsed.sort_values("start_datetime").reset_index(drop=True)

# match each gpx track to a row in parsed_workout_data
merge_cols = []
for i, row in df_track_info.iterrows():
    closest_match_idx = np.abs(workout_data_parsed['start_datetime'] - row["start_datetime"]).argmin()
    merge_cols.append(workout_data_parsed.iloc[closest_match_idx]["start_datetime"])
df_track_info["merge_col"] = merge_cols

# merge to get workout type
new = df_track_info.merge(workout_data_parsed[["start_datetime", "workoutActivityType"]], left_on="merge_col", right_on="start_datetime", suffixes=[None, "_y"])
# exclude all non-running workouts
new = new.loc[new["workoutActivityType"] == "HKWorkoutActivityTypeRunning"].drop(columns=["merge_col", "start_datetime_y", "workoutActivityType"]).reset_index(drop=True)

new.to_parquet("data/track_info.parquet")