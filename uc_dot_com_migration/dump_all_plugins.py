
import requests
import json, os, sys
from bs4 import BeautifulSoup
import logging

SOUP_PARSER = "html.parser"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

logger1 = logging.getLogger("dumpallplugins")

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
        if (adir[0] != "?" and adir[0] != "/"):
            itemname = adir.replace("/", "")
            listitems.append(itemname)
    listitems.sort()
    logger1.info(listitems)
    return listitems

# TODO: x.yyyy also check yyyy ! f.e. 6.86 is higher than 6.111 in this function, should be 6.111 higher!
# TODO: Check that the versionnumber makes sense, as there are several "version naming" conventions used!
def getversionnumber2(elem):
    return getversionnumber(elem, True)

def getversionnumber(elem, forsort=False):
    logger1.info(elem)
    split_tup = os.path.splitext(elem)
    logger1.info(split_tup)
    parts = split_tup[0].split("-")
    allnumparts = parts[-1].split(".")
    logger1.info(f"allnumparts={allnumparts}")
    for i in range(len(allnumparts)):
        numfilter = filter(str.isdigit, allnumparts[i])
        numstring = "".join(numfilter)
        if forsort: 
            numstring = numstring.zfill(10)
        allnumparts[i] = "".join(numstring)
        
    x = "0"
    if allnumparts[0].isnumeric():
        x = f'{allnumparts[0]}.'
        for i in range(1, len(allnumparts)):
            x = x + allnumparts[i]

    logger1.info(x)
    return float(x)

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
                pluginfiles.sort(key=getversionnumber2)
                oneplugin = {
                    "plugin_folder_name": item,
                    "files": pluginfiles,
                    "latestversion": getversionnumber(pluginfiles[-1]),
                }
                logger1.info(oneplugin)
                allplugins.append(oneplugin)
            else:
                logger1.warning(f"{item} is empty")
        else:
            logger1.warning (f"{item} is a zip.file not a directory")
    return allplugins

def main(argv):

    source_url = os.getenv("PLUGINFILES_SOURCE_URL")
    plugin_type = os.getenv("EXPORT_PLUGIN_TYPE")
    
    allplugins = []
    allplugins = getallplugins(source_url)

    adict = {"source_download_folder": source_url, "plugins": allplugins}
    with open (f"{plugin_type}-allplugins.json", "w") as f:
        json.dump(adict,f, indent=4)

    os._exit(0)
if __name__ == '__main__':
    main(sys.argv[1:])