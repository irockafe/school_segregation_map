import requests
import zipfile
import os
import pathlib

def dload_unzip(url, data_path): 
    # data_path is a Pathlib() object                                  
    # dowload file                    
    r = requests.get(url)
    fname = url.split('/')[-1]  # last thing after the slash  
    print(fname)
    with open(data_path/fname, 'wb') as f:
        f.write(r.content)                                  
    # unzip file
    zip_file = zipfile.ZipFile(data_path/fname)
    zip_file.extractall(data_path)                            
    zip_file.close()                                          

data_path = (pathlib.Path('/home/data'))
if not data_path.exists():
    pathlib.mkdir(data_path)
# Get the location data
loc_url = ('https://nces.ed.gov/programs/edge/data/' +
           'EDGE_GEOCODE_PUBLICSCH_1516.zip')
dload_unzip(loc_url, data_path)
# Get the racial breakdown data
racial_url = ('https://nces.ed.gov/ccd/Data/zip/' +
              'ccd_sch_052_1516_w_2a_011717_csv.zip')
dload_unzip(racial_url, data_path)
# Get the school lunch data
school_lunch_url = ('https://nces.ed.gov/ccd/Data/zip/' +
                    'ccd_sch_033_1516_w_2a_011717_csv.zip')
dload_unzip(school_lunch_url, data_path)
