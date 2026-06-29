import pandas as pd
import xml.etree.ElementTree as ET
import seasons

### Load APPLE HEALTH WORKOUT XML
filepath = '/Users/ryansponzilli/Developer/Python Projects/xc-routes/data/raw/export.xml'

# load file and parse into dictionary
root = ET.parse(filepath).getroot()

# extract the Workout entries
workout_data = pd.DataFrame([x.attrib for x in root.iter('Workout')])
workout_data.to_parquet("data/intermediate/workout_data.parquet")

# parse data types
workout_data['creationDate'] = pd.to_datetime(workout_data['creationDate'])
workout_data['startDate'] = pd.to_datetime(workout_data['startDate'])
workout_data['endDate'] = pd.to_datetime(workout_data['endDate'])
workout_data['duration'] = workout_data['duration'].astype(float)

# filter time period
workout_data = workout_data.loc[(workout_data['startDate'] >= pd.to_datetime(seasons.MIN_DATE, utc=True)) & (workout_data['startDate'] <= pd.to_datetime(seasons.MAX_DATE, utc=True))]

# get relevant data
workout_data = workout_data.loc[workout_data['sourceName'] != "Strava"]
workout_data = workout_data[["workoutActivityType", "creationDate", "startDate", "endDate", "duration", "durationUnit"]].rename(columns={"creationDate": "creation_datetime", "startDate": "start_datetime", "endDate": "end_datetime"})
workout_data = workout_data.sort_values("start_datetime").reset_index(drop=True)