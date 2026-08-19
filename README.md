# XC Routes GIS Project

## Overview
I ran cross country and track all four years that I was in high school, and I recorded every single run on my Apple Watch. I believe that this is a very unique trove of data that has the potential to be very interesting and very personal. I obtained the raw data by exporting my Apple Health data. This export gave me a 2.23 GB `.xml` file and a folder containing 1,232 `.gpx` files.

Please see the [this](results/showcase.html) document where I showcase the entire workflow of this project.

## Data Cleaning / Parsing Steps
* Load track file paths and extract the date from the file name
* Filter for tracks within my high school career
* Merge with workout XML to remove non-running tracks
* Year and Season bucketing
* GPX track data extraction
    * Start/end times and points
    * Pace, distance, duration, elevation change
    * Track lines with pauses detected and fixed
* *Route Detection*
    * Unsupervised Classification of Routes
    * Manually Create a Training Dataset
    * Supervised Classification of Routes
* Run Categorization & Merging
    * Detect and categorize doubles
    * *Detect and merge accidental splits* -> the same thing might accomplish both of these in one go
    * *Detect and merge workouts* -> the same thing might accomplish both of these in one go (do I want warmup/cooldown merged?)

## Data Quality Issues
### Activity Type
Biking, Walking, and Hiking activities may be mixed in. However, there are 8 GPX tracks that I could not link to an XML entry; I have assumed that they are indeed running workouts.

**Solution**: GPX tracks can be linked to workout entries in the health export XML file, which contains an activity type field.

### Accidental Splits
Sometimes during the middle of a run, I would accidently end the workout and have to start another one. These accidental splits should be recombined into a single run. (Example: March 22, 2023).

**Possible Solutions**: a run that starts and ends in an abnormal location, if the two activities are temporally continuous and spatially continuous, and if the combined segments resemble a known route.


### Pauses in Runs
In some runs, I would pause and not remember to unpause for quite a while, leading to gaps in the track. These should be separated into two track lines to avoid interpolation when displaying on a map.

**Solution**: Detect abnormally large gaps between consecutive points on a track using a threshold of 10 $\sigma$.

## Categorizations to Make

### Types of Run
#### Normal Run
Easy runs are 30-45 minutes at a moderate pace and often follow typical routes.

#### Long Run
Long runs are at least 50 minutes long and often follow typical routes.

#### Workout
Multiple segments of a workout get complicated. A workout consists of a single warmup segment, one or more workout segments, and a single cooldown segment (this could be further complicated by accidental splits). The warmup and cooldown segments should be flagged as such for later use in understanding the data. The workout segments should be combined together, having their track lines merged, and the activity should be flagged as a workout. Warmup and cooldown segments can be identified by their short length, typical routes, and by the fact that they precede or follow a workout. Workout segments can be identified by their faster pace or greater elevation change, and by the fact that they are preceeded by a warmup and followed by a cooldown.

### Route
Routes are segements of tracks that show up time and time again across the dataset. My strategy for route classification is to first do a pass of unsupervised clustering in order to see what all the routes are. Then, I will use the results to construct a training dataset. For each route, I will pick a single track line that best exemplifies that particular route. Then I will run a supervised learning algorithm to classify the routes in the entire dataset. A single run may contain more than one route, since sometimes routes are chained together.

### Year
* Freshman
* Sophomore
* Junior
* Senior

### Season
* Summer Training
* XC Season
* Winter Training
* Track Season

## Data Dictionary of Processed Data

### Year and Season Boundaries
* `year`
* `season`
* `start_date`
* `end_date`

### Region Boundaries
* `region_name`
* `region`: Shapely polygon

### Track Info
* `track_file`: The GPX track file.
* `track_file_datetime`: The timestamp embedded in `track_file`.
* `track_file_date`: The date of the `track_file_datetime`.

* `start_point`: The first point in the track.
* `end_point`: The last point in the track.
* `track_line`: The entire route.
* `start_time`: The timestamp of the first point in the track.
* `end_time`: The timestamp of the last point in the track.
* `duration`: The difference between `start_time` and `end_time`.
* `distance`: The total track distance traversed between `start_point` and `end_point`.

* `year`: The year of school the run occurred in.
* `season`: The season of the year the run occurred in

### Health Info
* `ActiveEnergyBurned`
* `HeartRate`
* `RunningSpeed`
* `VO2Max`

