import pyproj as pp
import pathlib
import pandas as pd
import numpy as np
from scipy import spatial
import pickle


# TODO refactor this into organize_data.py that calls fxns from organize_fxns.py 
#   it'll look cleaner then

def latlon_to_3d_coordinates(lat, lon, alt):
    # lat, lon, and alt are numpy arrays
    ecef = pp.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pp.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    # Default cartesian unit (ECEF) is meters
    x, y, z = pp.transform(lla, ecef, lon, lat, alt, radians=False)
    xyz_array = np.array([x,y,z]).T
    return xyz_array


# Go up one directory into data directory
data_path = (pathlib.Path('/home/data'))

# Combine the race, location, and school lunch data
df_race = (pd.read_csv(data_path / 'ccd_sch_052_1516_w_2a_011717.csv',
                       encoding='windows-1252')
             .set_index(['NCESSCH'])
           )

df_loc = (pd.read_excel(data_path /
                        'EDGE_GEOCODE_PUBLICSCH_1516' /
                        'EDGE_GEOCODE_PUBLICSCH_1516.xlsx')
            .set_index(['NCESSCH'])
            )
df_lunch = (pd.read_csv(data_path / 'ccd_sch_033_1516_w_2a_011717.csv',
                        encoding='windows-1252')
              .set_index(['NCESSCH'])
              [['TOTFRL', 'FRELCH', 'REDLCH']]  # Only select the columns with data
            )

data_raw = pd.concat([df_race, df_loc, df_lunch], axis=1)

# Clean up data-entry errors
# Drop Pre-K implicitly by not grabbin any of its columns
races = ['AM', 'AS', 'HI', 'BL', 'WH', 'HP', 'TR']
grades = (['KG'] + ['0%s' % i for i in range(1,10)] + 
  ['%s' % i for i in range(10,14)])
race_cols = pd.Index(['%s%s%s' % (race, grade, gender) 
              for race in races 
                for grade in grades
                  for gender in ['M', 'F']])
grade_cols = pd.Index(['KG'] + 
   ['G0%s' % grade for grade in range(1,10)] + 
   ['G%s'% i for i in range(10,14) ])
pre_k_m = race_cols[race_cols.str.contains('PKM')]
pre_k_f = race_cols[race_cols.str.contains('PKF')]
pre_k_cols = pre_k_m.union(pre_k_f)
race_cols = race_cols.drop(pre_k_cols)

# Get race and grade data only to filter and play with
data_race_grade = pd.concat([data_raw[grade_cols], data_raw[race_cols]],
                           axis=1)

data_race_grade = (data_race_grade[data_race_grade > 0]
                     .dropna(axis=0, how='all')
                     )
# separate into grade and race
data_grades = data_race_grade[grade_cols]
data_races = data_race_grade[race_cols]
median_grade = data_grades.median(axis=1)
# Remove grade columns < 10% of median 
grades_over_10p = data_grades.div(median_grade, axis=0) > 0.1
data_grades_filtered = data_grades[(grades_over_10p)]
# Eliminate race columns that have zero in their grade column b/c the grade column
# was an obvious outlier
for grade in grades:
    race_cols_in_grade = race_cols[race_cols.str.contains(grade)]
    num_students_race_sum = data_races[race_cols_in_grade].sum(axis=1)
    if grade in ['KG']:
        num_students = data_grades_filtered['%s' % grade]
    else:
        num_students = data_grades_filtered['G%s' % grade]
    idx_to_replace = num_students[(np.isnan(num_students) & (num_students_race_sum > 0))].index
    data_races.loc[idx_to_replace, race_cols_in_grade] = np.nan

# Now recombine together and dropnan again
data_filtered_again = (pd.concat([data_grades_filtered, data_races], axis=1)
                         .dropna(axis=0, how='all'))
raw_data_non_race_grade = (data_raw.drop(grade_cols.union(race_cols).union(pre_k_cols), axis=1)
                            .loc[data_filtered_again.index]
                            )
df = pd.concat([data_filtered_again, raw_data_non_race_grade], axis=1)

# remove any entries missing lat or lon info
# Losing some CT schools info
# TODO keep finding where the missing values are (CT)
# and update those in fix_data.py
no_lat = df[df['LAT1516'].isnull()].index
no_lon = df[df['LON1516'].isnull()].index
no_latlon = no_lat.union(no_lon)
df = df.drop(index=no_latlon)

# Convert lat-lon to xyz coordinates
lat = df['LAT1516'].values
lon = df['LON1516'].values
alt = np.zeros(df.shape[0])

xyz_array = latlon_to_3d_coordinates(lat, lon, alt)
xyz_df = pd.DataFrame(xyz_array, columns=['x', 'y', 'z'], 
                      index=df.index)
df = pd.concat([df, xyz_df], axis=1)

# Always create kd-tree at last step, otherwise indices 
# will be incorrect.
# Create kd-tree to find all schools within certain distances
kd_tree = spatial.KDTree(xyz_array)
pickle.dump(kd_tree, open(data_path / 'school_distances_kdTree.pkl', 'wb'))
mile2meter = 1609.34

# dump the data frame with organized_data
pickle.dump(df, open(data_path / 'organized_data.pkl', 'wb'))
