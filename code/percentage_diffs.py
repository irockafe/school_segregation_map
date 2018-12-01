import pandas as pd
import numpy as np
import argparse
import logging
import pickle
import time

class regional_racial_breakdown:
    def __init__(self, df_schools, df_neighbors):
        '''
        df_schools is a regular dataframe: school_id x races 
        df_neighbors is a multiIndex dataframe: (central school, neighbors) x races
        '''
        # This might be a bad idea in terms of memory... several gigabyte files
        assert type(df_neighbors.index) == pd.MultiIndex, 'df_neighbors should be multi-index'
        assert type(df_schools.index) == pd.core.indexes.numeric.Int64Index, \
                'df_schools should have be an Int64 index of NCESSHID numbers'
        self.racial_counts_neighbors = df_neighbors
        self.racial_counts_schools = df_schools
        # Get percentages for schools and neighbors immediately
        
        
    def school_racial_percentages(self):
        return (self.racial_counts_schools.div(
            self.racial_counts_schools.sum(axis=1), axis=0))
    
    def neighbor_racial_percentages(self):
        # Remember, neighbor racial percentages can be different
        # than school-racial percentages, because we only kept
        # the grades that matced the central school
        return (self.racial_counts_neighbors.div(
            self.racial_counts_neighbors.sum(axis=1), 
            level='neighbors', axis=0))
    
    def racial_percentage_differences(self):
        # Calculates the difference in racial percentages
        # between a central school and all its neighboring schools
        # Get percentage values for neighbors and schools
        df_neighbor_racial_percent = self.neighbor_racial_percentages()
        df_school_racial_percent = self.school_racial_percentages()
        return df_neighbor_racial_percent.subtract(df_school_racial_percent, level='central_school')

    def lunch_percentage_differences(self, central_schools,
            neighbor):
        # central schools is a (school x lunch_data) dataframe
        # neighbor is a ((central school, neighbor) x lunch_data) dataframe
        # Calculate the difference in percentages between central schools
        # and all their neighbors

        # TODO replace all negative values with nans in the organize_data phase
        central_schools[central_schools < 0] = np.nan
        neighbor[neighbor < 0] = np.nan
        percent_schools = central_schools.div(central_schools['TOTAL'],
                axis=0)
        # Remove incorrectly entered data
        too_high_schools = percent_schools[percent_schools > 1].dropna(how='all', axis=0).index
        percent_schools = percent_schools.drop(index=too_high_schools)
        # dropping those mis-entered schools
        neighbor = neighbor.drop(index=too_high_schools, level='neighbors')
        percent_neighbors = neighbor.div(neighbor['TOTAL'], axis=0,
                level='neighbors')
        return percent_neighbors.subtract(percent_schools,
                level='central_school')


# argparse points us to the pkl file
# python filename -f path -r radius
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file',
        help='Absolute path to pickled dictionary that contains\
                dict of dataframes of neighboring schools racial\
                breakdowns, and dict of series with central school\
                racial breakdown')
parser.add_argument('-r', '--radius',
        help='Radius of neighbors you searched for')
args = parser.parse_args()
radius = args.radius
fname = args.file
t1 = time.time()
data = pickle.load(open(fname, 'rb'))
t2 = time.time()
logging.basicConfig(filename='/home/logs/percent_diff_%s_miles' % radius,
        level=logging.DEBUG, filemode='w')
logging.info('Loaded %s, it took %s' % (fname, t2-t1))

shared_grades = data['race_counts_shared_grades']
just_school = data['race_counts_just_school']
# convert the dict of dataframes/series into df_schools and df_neighbors
# Create a school_id x race dataframe
df_schools = pd.concat(just_school.values(), keys=just_school.keys(),
        axis=1).T
logging.info('Made the school dataframe')
logging.info('Dataframe shape: {shape}'.format(shape=df_schools.shape))
pickle.dump(df_schools, 
        open('/home/data/race_counts_schools_%s.pkl' % radius, 'wb'))

# Create a multiindex (central school, neighbors) x race
df_neighbors = pd.concat(shared_grades.values(), keys=shared_grades.keys(),
        names=['central_school', 'neighbors'])
logging.info('Made the multiIndex df')
logging.info('MultiIndex df shape: {shape}'.format(shape=df_neighbors.shape))
pickle.dump(df_neighbors, 
        open('/home/data/race_counts_neighbors_%s.pkl' % radius, 'wb'))
# get percent differences between central school and its neighbors
regional_data = regional_racial_breakdown(df_schools, df_neighbors)
t1 = time.time()
racial_percent_diff = regional_data.racial_percentage_differences()
t2 = time.time()
logging.info('Got the percentage differences. It took %s' % (t2-t1))

# Get the lunch differences
central_school_lunch = data['lunch_data_just_school']
neighbor_lunch = data['lunch_data_shared_grades']
lunch_df = pd.concat(central_school_lunch.values(), keys=shared_grades.keys(),
        axis=1).T
logging.info('lunch Dataframe made. shape: {shape}'.format(shape=lunch_df.shape))
pickle.dump(lunch_df, 
        open('/home/data/lunch_counts_schools_%s.pkl' % radius, 'wb'))
lunch_neighbor_df = pd.concat(neighbor_lunch.values(),
        keys=neighbor_lunch.keys(), names=['central_school', 'neighbors'])
logging.info('lunch neighbor multiidex df. Shape: {shape}'.format(
    shape=lunch_neighbor_df.shape))
pickle.dump(lunch_neighbor_df, 
        open('/home/data/lunch_counts_neighbors_%s.pkl' % radius, 'wb'))
t1 = time.time()
lunch_differences = regional_data.lunch_percentage_differences(
        lunch_df, lunch_neighbor_df)
t2 = time.time()
logging.info('Got percent differences for schools. It took %s' % (t2-t1))
# pickle the result
# all_grades because lunch data isn't broken down by grade level
lunch_output = '/home/data/lunch_percent_diff_shared_grades_%s.pkl' % radius
output_path = '/home/data/racial_percent_diff_shared_grades_%s.pkl' % radius 
t1 = time.time()
pickle.dump(racial_percent_diff, open(output_path, 'wb'))
pickle.dump(lunch_differences, open(lunch_output, 'wb'))
t2 = time.time()
logging.info('pickled the percent diff files at \n%s\n%s\n\n\
        it took %s' % (output_path,
    lunch_output, t2-t1)) 

