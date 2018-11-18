import requests
import zipfile
import os
import pathlib
import logging

def dload_unzip(url, data_path): 
    # data_path is a Pathlib() object                                  
    # dowload file                    
    r = requests.get(url)
    fname = url.split('/')[-1]  # last thing after the slash  
    with open(data_path/fname, 'wb') as f:
        f.write(r.content)                                  
    # unzip file
    zip_file = zipfile.ZipFile(data_path/fname)
    zip_file.extractall(data_path)                            
    zip_file.close()                                          


data_path = (pathlib.Path('/home/data'))
if not data_path.exists():
    data_path.mkdir()
log_path = pathlib.Path('/home/logs')
if not log_path.exists():
    log_path.mkdir()
logging.basicConfig(filename=log_path / 'download_data.log',
        level=logging.DEBUG)
# Get the location data
loc_url = ('https://nces.ed.gov/programs/edge/data/' +
           'EDGE_GEOCODE_PUBLICSCH_1516.zip')
logging.info('Working on \n{url}'.format(url=loc_url))
dload_unzip(loc_url, data_path)
# Get the racial breakdown data
racial_url = ('https://nces.ed.gov/ccd/Data/zip/' +
              'ccd_sch_052_1516_w_2a_011717_csv.zip')
logging.info('\n\nWorking on {url}'.format(url=racial_url)) 
dload_unzip(racial_url, data_path)
# Get the school lunch data
school_lunch_url = ('https://nces.ed.gov/ccd/Data/zip/' +
                    'ccd_sch_033_1516_w_2a_011717_csv.zip')
logging.info('\n\nWorking on {url}'.format(url=school_lunch_url))
dload_unzip(school_lunch_url, data_path)
