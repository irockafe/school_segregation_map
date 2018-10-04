DOIT_CONFIG = {'check_file_uptodate': 'timestamp',
               'verbosity': 2}


def task_download_data():
    # Get the data
    # Location data - lat/long, zipcode, congressional district, etc
    # https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_1516.zip
    # (it's the .xlsx file)
    # Racial breakdown:
    # https://nces.ed.gov/ccd/Data/zip/ccd_sch_052_1516_w_2a_011717_csv.zip
    # School Lunch (SES estimate):
    # https://nces.ed.gov/ccd/Data/zip/ccd_sch_033_1516_w_2a_011717_csv.zip
    break


def task_organize_data():
    # get data into a good format
    break


def task_analyze_data():
    # do some of the analysis of the data
    break


def task_visualize():
    # make the visualizations from the analyses
    break
