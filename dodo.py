import pathlib
import pandas as pd

DOIT_CONFIG = {'check_file_uptodate': 'timestamp',
               'verbosity': 2,
               'failure-verbosity': 2}

# Assume baseline path is where dodo.py is located
PATH = pathlib.Path().absolute() 
# Number of miles around which to search for neighboring schools
RADII = [1, 2.5, 5, 7.5]
DATA_PATH = PATH / 'data'
CODE_PATH = PATH / 'code'

def task_download_data():
    # run download_data.py:
    yield {
        'targets': ['data/ccd_sch_033_1516_w_2a_011717.csv',
                    'data/ccd_sch_052_1516_w_2a_011717.csv',
                    'data/EDGE_GEOCODE_PUBLICSCH_1516/' +
                    'EDGE_GEOCODE_PUBLICSCH_1516.xlsx'
                    ],
        'file_dep': ['code/download_data.py'],
        'actions': ['python code/download_data.py'],
        'name': 'download_data'
          }


def task_organize_data():
    # get data into a good format
    # write it to a file
    yield {
       'targets': ['data/organized_data.pkl',  # dataframe with all info
                   'data/school_distances_kdTree.pkl'],  # kd-tree of distances 
       'file_dep': ['code/organize_data.py'],
       'actions': ['python code/organize_data.py'],
       'name': 'organize_data'
    }
 

def task_process_data():
    '''Go from a big shreadsheet into dictionary of 
        {'radius': radius, 'raw_race_data': {school_id: data},
        'racial_counts_data': {school_id: data}}
    '''
    for radius in RADII:
        yield {
            'targets':[DATA_PATH / ('all_schools_within_%s_miles.pkl' % radius),
                       DATA_PATH / ('regional_racial_compositions_%s_miles.pkl' 
                        % radius)],
            'file_dep':[CODE_PATH / 'process_data.py',
                        'data/organized_data.pkl',
                        'data/school_distances_kdTree.pkl'],
            'actions':['python code/process_data.py --radius %s' % radius],
            'name': 'find_neighboring_schools_{radius}'.format(radius=radius)
        }


def task_analyze_data():
    # do some of the analysis of the data
    pass


def task_visualize():
    # make the visualizations from the analyses
    pass
