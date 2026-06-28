import pandas as pd
import xml.etree.ElementTree as ET
import seasons

### Load APPLE HEALTH WORKOUT XML
filepath = '/Users/ryansponzilli/Developer/Python Projects/xc-routes/data/raw/export.xml'

# load file and parse into dictionary
root = ET.parse(filepath).getroot()

# extract the Workout entries
record_data = pd.DataFrame([x.attrib for x in root.iter('Record')])
record_data.to_parquet("data/raw_parquet/record_data.parquet")

# parse data types
record_data['creationDate'] = pd.to_datetime(record_data['creationDate'])
record_data['startDate'] = pd.to_datetime(record_data['startDate'])
record_data['endDate'] = pd.to_datetime(record_data['endDate'])
# some records do not measure anything, just count occurences
# filling with 1.0 (= one time) makes it easier to aggregate
record_data['value'] = record_data['value'].fillna(1.0)
# value is numeric, NaN if fails
record_data['value_num'] = pd.to_numeric(record_data['value'], errors='coerce')
# shorter observation names
record_data['type'] = record_data['type'].str.replace('HKQuantityTypeIdentifier', '')
record_data['type'] = record_data['type'].str.replace('HKCategoryTypeIdentifier', '')

# filter time period
record_data = record_data.loc[(record_data['startDate'] >= pd.to_datetime(seasons.MIN_DATE, utc=True)) & (record_data['startDate'] <= pd.to_datetime(seasons.MAX_DATE, utc=True))]

# get relevant data
record_data = record_data.loc[record_data['type'].isin(["ActiveEnergyBurned", "HeartRate", "VO2Max", "RunningSpeed"])]
record_data = record_data[["type", "value", "unit", "creationDate", "startDate", "endDate"]].rename(columns={"creationDate": "creation_date", "startDate": "start_date", "endDate": "end_date"})
record_data = record_data.sort_values("start_date").reset_index(drop=True)
record_data.to_parquet("data/parsed/record_data.parquet")