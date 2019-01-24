import argparse
import pandas as pd
import scipy.stats as stats
import pickle
import matplotlib.pyplot as plt

def segregation_pvals(neighbor_data, school_data):
    '''
    GOAL- run hypergeometric test, odds of drawing at least as many 
       students from one racial group as found in a school, given the 
       total population of that race, total population of the region,
       and the population of the school.
    INPUT:
        neighbor_data: pandas MultIndex df, (central-school, neighbor) x 
           race_data. 
        school-data: pandas df, school_id x race_data
    OUTPUT:
        output - a dataframe containing pvals for each school/race,
           (school_id x race_data)
    '''
    region_demographics = (neighbor_data.sum(level='central_school'))
    region_demographics += school_data.loc[region_demographics.index]
    region_population = region_demographics.sum(axis=1)
    school_demographics = school_data.loc[region_demographics.index]
    school_population = school_demographics.sum(axis=1)

    output = pd.DataFrame(index=school_demographics.index,
            columns = school_demographics.columns, dtype="float64")
    for race in school_demographics.columns:
        df = pd.concat([
            region_population, region_demographics[race],
               school_population, school_demographics[race]
               ], axis=1)
        df.columns = ['region_pop', 'region_race_pop', 'school_pop',
            'school_race_pop']
        assert((df['region_race_pop'] >= df['school_race_pop']).all())
        assert((df['region_pop'] >= df['school_pop']).all())
        pvals = stats.hypergeom.sf(k=(df['school_race_pop']-1),
            M=df['region_pop'],
            n=df['region_race_pop'],
            N=df['school_pop']
            )
        output[race] = pvals
    return output

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--radius',
        help='Radius of neighbors you search for')
parser.add_argument('--neighbors',
        help='Path to pickled multiIndex df containing counts of \
                all racial groups in neighboring schools \
                (central_school, neighbors) x race_data, in counts')
parser.add_argument('--school_data',
        help='Path to pickled df containing school racial counts data')

args = parser.parse_args()
radius = float(args.radius)
neighbor_path = args.neighbors
school_path = args.school_data

neighbor_data = pickle.load(open(neighbor_path, 'rb'))
school_data = pickle.load(open(school_path, 'rb'))

df_pvals = segregation_pvals(neighbor_data, school_data)
df_pvals.hist(grid=False, sharey=True, sharex=True, figsize=(9,9))
plt.savefig('/home/Figures/segregation_pvals_%s.pdf' % radius)
plt.close()

pickle.dump(df_pvals, open('/home/data/segregation_pvals_%s.pkl' % radius, 'wb'))
