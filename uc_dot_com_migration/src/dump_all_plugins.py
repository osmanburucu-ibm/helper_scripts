
# sourcery skip: avoid-builtin-shadow
import requests
import json, os, sys
from bs4 import BeautifulSoup
import logging

import uc_migration_utils as ucutil

SOUP_PARSER = "html.parser"
script_name = "dump_all_plugins"

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
format=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(format)
ch.setFormatter(format)
logger1 = logging.getLogger(script_name)


logger1.addHandler(fh)
logger1.addHandler(ch)


# TODO: Better documentation needed
# TODO: add logging

def getlistitems(url):
    logger1.info(url)
    listitems = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, SOUP_PARSER)
    ahrefs = soup.find_all("a",href=True)
    for ahref in ahrefs:
        adir = ahref['href']
        if adir[0] not in ["?", "/"]:
            itemname = adir.replace("./", "")
            itemname = itemname.replace("/", "")
            listitems.append(itemname)
    listitems.sort()
    logger1.info(listitems)
    return listitems

def getallplugins(url):
    logger1.info(url)
    allplugins = []
    listitems = []
    listitems = getlistitems(url)

    for item in listitems:
        logger1.info(f"item={item}")
        if item.find(".zip") == -1:
            newurl = f'{url}/{item}'
            pluginfiles = []
            pluginfiles = getlistitems(newurl)
            if (len(pluginfiles) > 0):
                pluginfiles.sort(key=ucutil.getversionnumber2)
                oneplugin = {
                    "plugin_folder_name": item,
                    "files": pluginfiles,
                    "latestversion": ucutil.getversionnumber(pluginfiles[-1]),
                }
                logger1.info(oneplugin)
                allplugins.append(oneplugin)
            else:
                logger1.warning(f"{item} is empty")
        else:
            logger1.warning (f"{item} is a zip.file not a directory")
    return allplugins

def main():

    config = ucutil.get_config()
    
    source_url = config["files_source_url"]
    plugin_type = config["plugin_type"]
    
    allplugins = []
    allplugins = getallplugins(source_url)

    adict = {"source_download_folder": source_url, "plugins": allplugins}
    with open (f"{plugin_type}-allplugins.json", "w") as f:
        json.dump(adict,f, indent=4)

    os._exit(0)
if __name__ == '__main__':
    #main(sys.argv[1:])
    main()