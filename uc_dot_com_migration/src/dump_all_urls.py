import os, re
import csv
import pathlib
import logging
import uc_migration_utils as ucutil


SOUP_PARSER = "lxml" #"html.parser"
script_name = "dump_all_urls"

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

HREF_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))" #r'http[s]?://(?:[a-zA-Z]|\d|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' 
# r'(https?://[^\s]+)
def get_fixed_url (url):
    fixed_url = url
    if fixed_url[-1] == ".": fixed_url = fixed_url[:-1]
    if fixed_url[-1] == ")": fixed_url = fixed_url[:-1]
    if fixed_url[-1] == ">": fixed_url = fixed_url[:-1]
    if fixed_url[-1] == "*": fixed_url = fixed_url[:-1]
    if fixed_url[-1] == "*": fixed_url = fixed_url[:-1]
    return fixed_url

def get_all_urls_in_file(subdir,file):
    urls_in_file=[]
    if (pathlib.Path(file).suffix != ".md"):
        return urls_in_file
    if ("downloads.md" in file): return urls_in_file
    
    logger1.info(f"Checking {subdir}/{file}")
    with open (f"{subdir}/{file}") as f:
        for line in f:
            if urls := re.findall(HREF_REGEX, line):
                logger1.info(f"urls={urls}")
                for ur in urls:
                    logger1.info(f"ur={ur}")
                    for u in ur:
                        logger1.info(f"u={u}")
                        if u: urls_in_file.append(u)
    return urls_in_file

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def main():
    config = ucutil.get_config()

    rootdir=ucutil.get_target_doc_path(config, "", level=ucutil.DOC_LEVEL_PLUGIN_README)
    logger1.info(f"Rootdir={rootdir}")
    all_urls = []
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            # Debug
#            if ("WebSphereConfiguration" not in subdir): continue
            urls_in_file = get_all_urls_in_file(subdir,file)
            for url in urls_in_file:
                test=["",""]
                logger1.info(f"urls_in_file_url={url}")
                if not url: continue
                # skip url links to known plugin file repos
                if ("https://raw.githubusercontent.com/UrbanCode/IBM-UC" in url): continue
                logger1.info(f"append={url}")
                test[0]=f"{subdir}/{file}"
                test[1]=url # get_fixed_url(url)
                logger1.info(f"test={test}")
                all_urls.append(test)
            
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    plugin_type = config[ucutil.EXPORT_PLUGIN_TYPE]
    all_urls_header = ['file', 'url', 'active', 'new_url']
    with open (f"{workfolder}/{plugin_type}-all_urls.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(all_urls_header)
        writer.writerows(all_urls)

    os._exit(0)
    
if __name__ == '__main__':
    main()    