import pandas as pd
import xml.etree.ElementTree as ET
import seasons

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
workout_data_parsed.to_csv("data/workout_data.csv",index=False)