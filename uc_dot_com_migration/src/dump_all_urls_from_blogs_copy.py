import os, re
import csv
import pathlib
import logging
import uc_migration_utils as ucutil


# SOUP_PARSER = "html.parser" #"lxml" #"html.parser"
script_name = "dump_all_urls_from_blogs_copy"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{script_name}.log", "w+")
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
    if (pathlib.Path(file).suffix != ".html"):
        return urls_in_file
    logger1.info(f"Checking {subdir}/{file}")
    with open (f"{subdir}/{file}") as f:
        for line in f:
            if urls := re.findall(HREF_REGEX, line):
                for url in urls:
                    urls_in_file.extend(url)
                # urls_in_file.extend(urls)
                    logger1.info(f"urls={url}")
    return urls_in_file

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def main():
    config = ucutil.get_config()
    rootdir = f"{config[ucutil.BLOGS_DIR]}/"
    
    logger1.info(f"Rootdir={rootdir}")
    all_urls = []
    unique_urls =  set()
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
                unique_urls.add(url)
                test[0]=f"{subdir}/{file}"
                test[1]=url # get_fixed_url(url)
                logger1.info(f"test={test}")
                all_urls.append(test)
    logger1.info(f"unique_urls={unique_urls}")
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    all_urls_header = ['file', 'url', 'active', 'new_url']
    with open (f"{workfolder}/RELEASE_NOTES-all_urls.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(all_urls_header)
        writer.writerows(all_urls)
    with open (f"{workfolder}/RELEASE_NOTES_UNIQUE-all_urls.csv", "w") as f:
        # writer = csv.writer(f)
        #writer.writerow(['url', 'active', 'new_url'])
        for u in unique_urls:
            logger1.info(f"u={u}")
            # writer.write(f"{u},,\n")
            x = u.replace("http://www.urbancode.com", "")
            x = x.replace("https://developer.ibm.com/urbancode/wp-content/uploads/sites/16/2016/09/","")
            x = x.replace("2017/08/","")
            x = x.replace("2016/10/","")
            if (x == u): x=""
            f.write(f"{u},NO,,{x}\n")
    os._exit(0)
    
if __name__ == '__main__':
    main()    