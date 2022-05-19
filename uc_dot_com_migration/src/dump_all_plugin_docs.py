# sourcery skip: avoid-builtin-shadow
from cgitb import text
import json, os, sys
from tabnanny import check
from github import Github
from bs4 import BeautifulSoup
import requests
import re
import logging
import uc_migration_utils as ucutil


SOUP_PARSER = "html.parser"
script_name = "dump_all_plugin_docs"

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


def remove_tags(taggedcontent):
    for data in taggedcontent(['style', 'script']):
        data.decompose()
    mycontent = ''.join(taggedcontent.stripped_strings)
    logger1.info(f"remove_tags content: {mycontent}")
    return  mycontent

def get_content (misosoup):
    mydiv = misosoup.find("div", {"id":"container"})
    mycontent = remove_tags(mydiv)
    logger1.info(f"get_content: {mycontent}")
    return mycontent

## sanitize plugin doc link, as item is like this "<a href="https://www.urbancode.com/plugin/devops-insights-deployment-risk-analytics-dra/">Go to Plugin</a>"
def get_plugin_doc_link(plugin_item):
    item = plugin_item.find(class_="uc-grid-link")
    mystring = ""
    mystring = ''.join(map(str,item))
    doc_link = re.search("(?P<url>https?://[^\s]+)", mystring)["url"]
    doc_link = doc_link.replace('/\">Go', '')
    if (doc_link[-1]=="/"):
        doc_link = doc_link[:-1]
    logger1.info(f"get_plugin_doc_link: {doc_link}")
    return doc_link

def get_full_doc_link (response):
    soup = BeautifulSoup(response.text, SOUP_PARSER)

    linkelement = soup.find_all("div", {"class": "plugin-detail-content"})
    plugin_full_doc_link = ""
    for item in linkelement:
        if sitem := item.find("a", string="Documentation"):
            logging.debug(f"sitem: {sitem}")
            plugin_full_doc_link=sitem['href']
            if (plugin_full_doc_link[-1]=="/"):
                plugin_full_doc_link = plugin_full_doc_link[:-1]
            logger1.info(f"get_plugin_doc_link: {plugin_full_doc_link}")
    return plugin_full_doc_link

def get_full_doc_folder_name(response):
    doc_link = get_full_doc_link(response)
    if (doc_link == ""): doc_link = "/"
    urlparts = doc_link.split("/")
    logger1.debug(f"URLParts= {urlparts}")
    doc_folder_name = urlparts[-1]
    logger1.info(f"doc_foler_name={doc_folder_name}")
    return doc_folder_name 

def get_doc_folder_name_from_link(doc_link):
    logger1.info(f"link provided={doc_link}")
    urlparts = doc_link.split("/")
    logger1.info(f"URLParts= {urlparts}")
    doc_folder_name = urlparts[-1]
    logger1.info(f"doc_foler_name={doc_folder_name}")
    return doc_folder_name 


def check_plugin_type(plugin_item, plugin_type):
    item = plugin_item.find(class_="uc-grid-product").text.strip()
    logger1.info(f"check_plugin_type: {plugin_type} - item: {item}")
    return (plugin_type in item)

def isright_plugin_type(plugin_item, plugin_type):
    item = plugin_item.find("div", {"id":"product"})
    logger1.info(f"is_right_plugin_type: {plugin_type} - item: {item}")
    return (plugin_type in str(item))

# get documentation only for specific plugin tpyes
# UDB = ubuildplugins
def get_documentation(plugin_item, plugin_type):
    plugin_doc_link = get_plugin_doc_link(plugin_item)
    response2=requests.get(plugin_doc_link)
    soup2 = BeautifulSoup(response2.text,SOUP_PARSER)
    mycontent = ""
    # check if for right plugin_type if not exit 
    if isright_plugin_type (soup2, plugin_type):
        # get the short info content (for the overview page of all plugins)
        mycontent = get_content(soup2)
        logger1.info(f"get_documentation: {mycontent}")
    return mycontent

def get_plugin_name(response):
    plugin_name = ""
    soup = BeautifulSoup(response.text, SOUP_PARSER)
    plugin_name = soup.select('h1.entry-title')[0].text.strip()
    logger1.info(f"get_plugin_name={plugin_name}")
    return plugin_name

# get the folder name from the download url, will be used to recreate the docs folder structure same as for the files subfolders
def get_plugin_folder_name(response):
    urlpartsindex = -1
    soup = BeautifulSoup(response.text, SOUP_PARSER)
    linkelement = soup.find(id='uc-download-archive')
    plugin_folder_name = (
        linkelement["data-src"] if (linkelement is not None) else ""
    )
    if not plugin_folder_name:
#         <a class="btn btn-primary" id="info-button" href="https://public.dhe.ibm.com/software/products/UrbanCode/plugins/ibmucr/ucr-plugin-deploy/ucr-plugin-deploy-1.1053195.zip" target="_blank">
#            Download          </a>
        linkelement = soup.find(id = "info-button")
        plugin_folder_name=(linkelement["href"] if (linkelement is not None) else "")
        if ("urbancode.com" not in plugin_folder_name): plugin_folder_name = ""
        urlpartsindex = -2
        logger1.info("searched for dowloadlink, as not other available")
    logger1.info(f"get_plugin_folder_name={plugin_folder_name}")
    urlparts = plugin_folder_name.split("/")
    logger1.info(f"get_plugin_folder_name: URLParts= {urlparts}")
    if len(urlparts) >1 :
        plugin_folder_name= urlparts[urlpartsindex]
    logger1.info(f"plugin_folder_name = {plugin_folder_name}")
    return  plugin_folder_name

# <div class="plugin-detail-content">  <p><a href="https://www.urbancode.com/plugindoc/accurev/">Documentation</a></p>
def extract_tabs(plugin_doc_link):
    doctabs= []
    response=requests.get(plugin_doc_link)
    soup = BeautifulSoup(response.text,SOUP_PARSER)

    alltabs = soup.find_all("a", {"class": "nav-link", "role":"tab"})
    for tab in alltabs:
        logger1.info(f"tab: {tab['href']} and {tab.contents}")
        atab = {"name": tab.contents[0], "tab_id": tab["href"]}
        doctabs.append (atab)
    return doctabs


def get_doc_tabs(response):
    doctabs = []
    soup = BeautifulSoup(response.text, SOUP_PARSER)

    linkelement = soup.find_all("div", {"class": "plugin-detail-content"})
    plugin_doc_link = ""
    for item in linkelement:
        if sitem := item.find("a", string="Documentation"):
            logger1.info(f"sitem: {sitem}")
            plugin_doc_link=sitem['href']
    if plugin_doc_link:
        # extract the doctabs
        logger1.info(f"getdoctabs found {plugin_doc_link} ")
        doctabs = extract_tabs(plugin_doc_link)
    return doctabs
                  
def get_all_plugin_docs(source_url):
    logger1.info(f"Plugin URL: {source_url}")

    response = requests.get(source_url)
    soup = BeautifulSoup(response.text, SOUP_PARSER)
    plugin_type = os.getenv("EXPORT_PLUGIN_TYPE")

    allplugindocs = []

    # iterate over all plugin entries (as articles)
    list_of_plugins = soup.find_all("article", class_="uc-grid-item")
    for plugin_item in list_of_plugins:
        logger1.debug(f"plugin_item={plugin_item}")
        if (check_plugin_type(plugin_item, plugin_type)):
            plugin_doc_link = ""
            plugin_doc_link = get_plugin_doc_link(plugin_item)
            logger1.info(plugin_doc_link)

            response2 = requests.get(plugin_doc_link)
            oneplugin = {ucutil.NAME_PLUGIN_NAME: get_plugin_name(response2)}
            oneplugin[ucutil.NAME_PLUGIN_FOLDER_NAME]= get_plugin_folder_name(response2)
            oneplugin[ucutil.NAME_DOC_FOLDER_NAME]= get_doc_folder_name_from_link(plugin_doc_link)
            oneplugin[ucutil.NAME_DOCUMENTATION_NAME]=get_full_doc_folder_name(response2)
            oneplugin[ucutil.NAME_DOC_TABS]= get_doc_tabs(response2)
            allplugindocs.append(oneplugin)
    return allplugindocs

def main():
    
    config = ucutil.get_config()
    source_url = config[ucutil.PLUGIN_LIST_URL]
    plugin_type = config[ucutil.EXPORT_PLUGIN_TYPE]

    allplugindocs = []
    allplugindocs = get_all_plugin_docs(source_url)

    adict = {
        ucutil.EXPORT_SOURCE_URL: source_url, 
        ucutil.EXPORT_SOURCE_OVERVIEW_URL: config[ucutil.PLUGIN_OVERVIEW_URL], 
        ucutil.EXPORT_SOURCE_DOCUMENTATION_URL: config[ucutil.PLUGIN_DOCUMENTATION_URL], 
        ucutil.EXPORT_SOURCE_DOWNLOAD_FOLDER: config[ucutil.PLUGINFILES_SOURCE_URL], 
        ucutil.NAME_PLUGIN_LIST_NAME: allplugindocs
    }

    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    
    with open (f"{workfolder}/{plugin_type}-allplugindocs.json", "w") as f:
        json.dump(adict,f, indent=4)


if __name__ == '__main__':
    # main(sys.argv[1:])
    main()