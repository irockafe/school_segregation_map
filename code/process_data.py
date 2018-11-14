# Convert a big-ass spreadsheet of racial data into 
# a dictionary containing racial breakdowns (count and proportion)
# and free-reduced lunch breakdwons.
# Racial breakdowns find
# all schools that are BOTH within a given radius from the school.
# AND share at least one grade in common with that school.
# The racial comparisons are then only made on grades present in the school
# that is the center of radius (the school_id that is the dictionary key)
# In my mind there's no reason to compare a high school to an elementary
# b/c that info is not actionable (can't integrate a high school with 
# kids from elementrary school - also, bad-90s baby-genius screenplay)
#
# NOTE the racial comparisons are only between shared grades, but 
# Lunch data isn't disaggregated by grade, so that is school-wide
# Could muck with the analysis a bit, going to include a key with
# all the races from a school, not just those with same grades

import pickle
import pandas as pd
import numpy as np
import pathlib
import time
import argparse
import sys
if '/home/code' not in sys.path:
    sys.path.append('/home/code')
import analyze_segregation


def count_races(raw_race_data, school_id):
    races = ['AM', 'AS', 'HI', 'BL', 'WH', 'HP', 'TR']
    racial_counts = pd.DataFrame(index=raw_race_data.index, columns=races)
    # raw_race_data = self.raw_race_data()
    for race in races:
        #one_race_population = student_races[student_races.index.str.contains(race)]
        one_race_population = (raw_race_data.loc[:,raw_race_data.columns.str.contains(race)]
                               .sum(axis=1)
                              )
        racial_counts[race] = one_race_population
    return racial_counts


def get_regional_breakdown(data, raw_race_data, all_race_columns, all_nearby_schools):
    # data - is the dataframe with everything in it (for the School() object and finding lunch
    # race_data is data from all the columns for racial groups in each grade
    # all_race_columns is all the columns in race_data
    race_breakdown_region_all_schools = {'radius': radius, 
                                        'race_counts_all_neighbors': {},
                                        'race_proportions_all_neighbors': {},
                                        'race_counts_shared_grades': {},
                                        'race_proportions_shared_grades': {},
                                        'school_disimilarity_shared_grades': {},
                                        'raw_lunch_data': {},
                                        'lunch_proportions':{}}
    t1 = time.time()
    kd_tree = None  # placeholder b/c don't need it in the School() object
    lunch_data_all = data[['TOTAL', 'TOTFRL', 'FRELCH', 'REDLCH']]
    for i, school_id in enumerate(data.index):
        if (i+1) % 5000 == 0:
            print('{num} loops took {t:.3f}'.format(
                            num=i+1, t=(time.time() - t1)))
        school = analyze_segregation.School(school_id, data, kd_tree)
        grades_served = school.grades_served().str.replace('G', '')
        #print(grades_served)
        # Given grades served, get all the columns containing race data
        race_grade_cols = pd.Index([])
        for grade in grades_served:
            race_grade_cols = race_grade_cols.union(all_race_columns[all_race_columns.str.contains(grade)])

        # get race data for all neighbors of current school_id
        # Neighbors are any schools within radius
        # we drop those that don't share any grades later, when creating race_data
        neighbor_ids = raw_race_data.iloc[all_nearby_schools[i],:].index
        race_data_all_grades = (raw_race_data.loc[neighbor_ids,:])
        race_counts_all_neighbors = count_races(race_data_all_grades, school_id)
        race_proportions_all_neighbors = race_counts_all_neighbors.div(
                race_counts_all_neighbors.sum(axis=1), axis=0)
        race_breakdown_region_all_schools['race_counts_all_neighbors'][school_id] = race_counts_all_neighbors
        race_breakdown_region_all_schools['race_proportions_all_neighbors'][school_id] = race_proportions_all_neighbors
        '''
        # This is about 3x faster than doing .loc[row, column]. not sure why
        # The dropna will remove any neighbors that don't have grades in common with school_id
        race_data = (raw_race_data.loc[neighbor_ids, :]
                     .loc[:,race_grade_cols]
                     .dropna(axis=0, how='all')
                    )
        '''
        # The dropna will remove any neighbors that don't have grades in common with school_id
        # b/c race_grade_cols only contains columns that contain grades in school_id
        race_data = (race_data_all_grades.loc[:, race_grade_cols]
                                        .dropna(axis=0, how='all')
                     )
        #print(race_data)
        # Count up each racial group
        race_counts = count_races(race_data, school_id)
        race_proportions = race_counts.div(race_counts.sum(axis=1), axis=0)
        disimilarity_shared_grades = ((race_proportions.loc[school_id] - race_proportions)
                .drop(index=school_id))
        race_breakdown_region_all_schools['race_counts_shared_grades'][school_id] = race_counts
        race_breakdown_region_all_schools['race_proportions_shared_grades'][school_id] = race_proportions
        race_breakdown_region_all_schools['school_disimilarity_shared_grades'][school_id] = disimilarity_shared_grades

        ## Lunch data
        # Again, implicitly select only schools with at least one grade in common
        lunch_data_counts = (lunch_data_all.loc[race_data.index,:])
        # TOTAL is the column with all the students
        lunch_data_proportions = (lunch_data_counts.div(lunch_data_counts['TOTAL'],axis=0)
                                                    .drop(columns=['TOTAL'])
                                                    )
        race_breakdown_region_all_schools['raw_lunch_data'][school_id] = lunch_data_counts
        race_breakdown_region_all_schools['lunch_proportions'][school_id] = lunch_data_proportions
    return race_breakdown_region_all_schools


parser = argparse.ArgumentParser()
parser.add_argument('-r', '--radius',
    help='Number of miles from school you want to search for other schools ')
args = parser.parse_args()

# Get the data and kd_tree
raw_data_path = '/home/data/organized_data.pkl'
kd_tree_path = '/home/data/school_distances_kdTree.pkl'
data = pickle.load(open(raw_data_path, 'rb'))
kd_tree = pickle.load(open(kd_tree_path, 'rb'))

# Define columns where racial counts are held
data_path = pathlib.Path('/home/data')
races = ['AM', 'AS', 'HI', 'BL', 'WH', 'HP', 'TR']
number_grades = ['0%s' % i for i in range(1,10)] + ['%s' % i for i in range(10,14)]
grades = ['KG'] + number_grades
all_race_columns = pd.Index(['%s%s%s' % (race, grade, gender) for race in races
                         for grade in grades
                            for gender in ['M', 'F']]
                     )

radius = float(args.radius)
mile2meter = 1609.34
filename = 'all_schools_within_%s_miles.pkl' % radius
# This should be done in a separate script so that pydoit can keep track of dependencies
try:
    all_nearby_schools = pickle.load(open(data_path / filename, 'rb'))
except FileNotFoundError:
    # filenotfoudn error
    all_nearby_schools = kd_tree.query_ball_tree(kd_tree, radius*mile2meter)
    # save to file
    pickle.dump(all_nearby_schools, open(data_path / filename, 'wb'))
    print('''Couldnt find the nearby schools file - all_schools_within_%s_miles.pkl
        Generating it now...''' % radius)

raw_race_data = data[all_race_columns]
output = get_regional_breakdown(data, raw_race_data, all_race_columns, all_nearby_schools)
filename = 'regional_racial_compositions_%s_miles.pkl' % radius
pickle.dump(output, open(data_path / filename, 'wb'))
