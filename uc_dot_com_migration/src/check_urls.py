import os
import csv
import requests
import logging
import uc_migration_utils as ucutil
import validators


script_name = "check_urls"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{script_name}.log")
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
logger1 = logging.getLogger(script_name)


logger1.addHandler(fh)
logger1.addHandler(ch)

def check_if_active(url):
    #Get Url
    try:
        get = requests.get(url, timeout=5)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return "NOT REACHABLE"
    
    return "YES" if get.status_code == 200 else f"NO {get.status_code}"

def main():
    config = ucutil.get_config()
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    all_urls = []
    with open(f'{workfolder}/MERGED-UNIQUE-all_urls.csv', "r",encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter=";")
        all_urls = list(reader)
        
    for item in all_urls:
        logger1.info(f"item={item}")
        if ("URL" in item[0]): continue
        item[1] = check_if_active(item[0]) if validators.url(item[0]) else "INVALID"
        logger1.info(f"updated item={item}")
        
    #logger1.info(f"checked ={all_urls}")
    
    with open(f'{workfolder}/MERGED-UNIQUE-CHECKED-all_urls.csv', "w") as csv_file:
        write = csv.writer(csv_file)
        write.writerows(all_urls)
    
    os._exit(0)
    
if __name__ == '__main__':
    main()    