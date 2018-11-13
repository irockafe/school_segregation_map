# Convert a big-ass spreadsheet of racial data into 
# a dictionary containing racial breakdowns (count and proportion)
# for all schools within a given radius of centered school.

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


def get_regional_breakdown(data, raw_race_data, all_race_columns):
    # data - is the dataframe with everything in t for the School() object
    # race_data is data from all the columns for racial groups in each grade
    # all_race_columns is all the columns in race_data
    race_breakdown_region_all_schools = {'radius': radius, 'raw_race_data': {},
                                        'racial_counts_data': {}}
    t1 = time.time()
    kd_tree = None  # placeholder b/c don't need it in the object
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
        #print('race grdae columns\n', race_grade_cols)

        # get race data for all neighbors only for the grades served by current target school
        neighbor_ids = raw_race_data.iloc[all_nearby_schools[i],:].index
        #print(neighbors)
        # This is about 3x faster than doing .loc[row, column]. not sure why
        race_data = (raw_race_data.loc[neighbor_ids, :]
                     .loc[:,race_grade_cols]
                     .dropna(axis=0, how='all')
                    )
        #print(race_data)
        # Count up each racial group
        race_counts = count_races(race_data, school_id)
        race_breakdown_region_all_schools['raw_race_data'][school_id] = race_data
        race_breakdown_region_all_schools['racial_counts_data'][school_id] = race_counts
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
output = get_regional_breakdown(data, raw_race_data, all_race_columns )
filename = 'regional_racial_compositions_%s_miles.pkl' % radius
pickle.dump(output, open(data_path / filename, 'wb'))
