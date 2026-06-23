# XC Routes GIS Project

## Goals
* Primary Goal: Understand the geographic distribution of my runs
    * Visualize where in the St. Charles area all of my runs are distributed
    * Group routes together, and get route statistics
* Secondary Goal: Understand how my running stats changed over time
    * Derive distance, speed, workouts
    * Understand fitness trends



## Data Quality Issues

### Activity Type
Biking, Walking, and Hiking activities may be mixed in. Solved by linking GPX tracks to workout entries in the XML file. However, there are 8 GPX tracks that I could not link to an XML entry; I have assumed that they are indeed running workouts.

### Accidental Splits
Accidental splits should be recombined into a single run. Here are some possible ways to detect accidental splits: a run that starts and ends in an abnormal location, if the two activities are temporally continuous and spatially continuous, and if the combined segments resemble a known route.

Example: March 22, 2023

### Pauses in Runs
In some runs, I would pause and not remember to unpause for quite a while, leading to gaps in the track. These should be separated into two track lines to avoid interpolation when displaying on a map.


## Categorizations to Make

### Types of Run
#### Easy Run
Easy runs are 30-45 minutes at a moderate pace and often follow typical routes.

#### Double
A double is a second run in a single day, separated by a large time period. The data indicates that a separation of 5 hours is a clean cutoff. Both runs can be considered as a double.

#### Long Run
Long runs are at least 50 minutes long and often follow typical routes.

#### Workout
Multiple segments of a workout get complicated. A workout consists of a single warmup segment, one or more workout segments, and a single cooldown segment (this could be further complicated by accidental splits). The warmup and cooldown segments should be flagged as such for later use in understanding the data. The workout segments should be combined together, having their track lines merged, and the activity should be flagged as a workout.

Warmup and cooldown segments can be identified by their short length, typical routes, and by the fact that they precede or follow a workout.

Workout segments can be identified by their faster pace or greater elevation change, and by the fact that they are preceeded by a warmup and followed by a cooldown.

#### Race
A race is short, fast, and accompanied by a warmup and cooldown. Most races were not recorded by my watch, but a small number were, along with unoffical time trials.

### Route
* School
    * Lake Loop
    * Dog Leg
    * Persimmon
    * Buddy's
    * Duke's
    * River Trail
    * Cornerstone
    * K's Loop
* Home
* Mount Saint Mary's
* Leroy Oakes
    * Course
* Great West
* Potowatomie
    * Double Tunnel
* Meets

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

