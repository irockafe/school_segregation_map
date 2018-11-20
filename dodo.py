import pathlib
import logging

logging.basicConfig(level=logging.DEBUG, 
        handlers=[logging.FileHandler("doit.log", mode='w', delay=False),
            #logging.StreamHandler(stream=sys.stdout)
            ])

DOIT_CONFIG = {'check_file_uptodate': 'timestamp',
               'verbosity': 2,
               'failure-verbosity': 2}

# Assume baseline path is where dodo.py is located
PATH = pathlib.Path().absolute() 
# Number of miles around which to search for neighboring schools
RADII = [1, 2.5, 5, 7.5, 15, 20]
DATA_PATH = PATH / 'data'
CODE_PATH = PATH / 'code'
LOG_PATH = PATH / 'logs'
for path in [DATA_PATH, CODE_PATH, LOG_PATH]: 
    if not path.exists():
        path.mkdir()

def task_download_data():
    # run download_data.py:
    yield {
        'targets': [DATA_PATH / 'ccd_sch_052_1516_w_2a_011717.csv',
            DATA_PATH / 'ccd_sch_033_1516_w_2a_011717.csv',
            DATA_PATH / 'EDGE_GEOCODE_PUBLICSCH_1516' / 'EDGE_GEOCODE_PUBLICSCH_1516.xlsx'],
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
       'actions': ['python code/organize_data.py &> %s' % (LOG_PATH / 'organize_data.log')],
       'name': 'organize_data'
    }
 

def task_regional_breakdown():
    '''
    Get a xarray dataset, where each variable is a school, dims = school x race, 
    and coordinates are school_id and racial group
    '''
    # Using floats to match with process_data, which names files with floats
    for radius in RADII:
        radius = float(radius)
        yield {
            'targets':[DATA_PATH / ('racial_composition_shared_grades_%s_miles.pkl' % radius),
                       DATA_PATH / ('racial_composition_shared_grades%s_miles.pkl' % radius),
                       DATA_PATH / ('lunch_data_shared_grades_%s_miles.pkl' % radius),
                       DATA_PATH / ('lunch_data_all_neighbors_%s_miles.pkl' % radius)
                       ],
            'file_dep':[CODE_PATH / 'regional_racial_breakdown.py',
                        'data/organized_data.pkl',
                        'data/school_distances_kdTree.pkl'
                        ],
            'actions':['python code/regional_racial_breakdown.py --radius {rad}'.format(rad=radius)],
            'name': 'regional_racial_breakdown_{radius}'.format(radius=radius)
        }


def task_analyze_data():
    # do some of the analysis of the data
    pass


def task_visualize():
    # make the visualizations from the analyses
    pass
