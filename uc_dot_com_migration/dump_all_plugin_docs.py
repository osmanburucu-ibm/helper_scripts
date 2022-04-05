from cgitb import text
import json, os, sys
from tabnanny import check
from github import Github
from bs4 import BeautifulSoup
import requests
import re
import logging

SOUP_PARSER = "html.parser"

# logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

def remove_tags(taggedcontent):
    for data in taggedcontent(['style', 'script']):
        data.decompose()
    mycontent = ''.join(taggedcontent.stripped_strings)
    logging.debug(f"remove_tags content: {mycontent}")
    return  mycontent

def get_content (misosoup):
    mydiv = misosoup.find("div", {"id":"container"})
    mycontent = remove_tags(mydiv)
    logging.debug(f"get_content: {mycontent}")
    return mycontent

## sanitize plugin doc link, as item is like this "<a href="https://www.urbancode.com/plugin/devops-insights-deployment-risk-analytics-dra/">Go to Plugin</a>"
def get_plugin_doc_link(plugin_item):
    item = plugin_item.find(class_="uc-grid-link")
    mystring = ""
    mystring = ''.join(map(str,item))
    doc_link = re.search("(?P<url>https?://[^\s]+)", mystring).group("url")
    doc_link = doc_link.replace('/\">Go', '')
    logging.debug(f"get_plugin_doc_link: {doc_link}")
    return doc_link

def get_doc_folder_name(plugin_doc_link):
    doc_folder_name = ""
    urlparts = plugin_doc_link.split("/")
    logging.debug(f"get_doc_folder_name: URLParts= {urlparts}")
    doc_folder_name = urlparts[-1]
    return doc_folder_name 

def check_plugin_type(plugin_item, plugin_type):
    item = plugin_item.find(class_="uc-grid-product").text.strip()
    logging.debug(f"check_plugin_type: {plugin_type} - item: {item}")
    return (plugin_type in item)

def isright_plugin_type(plugin_item, plugin_type):
    item = plugin_item.find("div", {"id":"product"})
    logging.debug(f"is_right_plugin_type: {plugin_type} - item: {item}")
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
        logging.debug(f"get_documentation: {mycontent}")
    return mycontent

def get_plugin_name(response):
    plugin_name = ""
    soup = BeautifulSoup(response.text, SOUP_PARSER)
    plugin_name = soup.select('h1.entry-title')[0].text.strip()
    logging.info(f"get_plugin_name={plugin_name}")
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
        logging.info("searched for dowloadlink, as not other available")
    logging.info(f"get_plugin_folder_name={plugin_folder_name}")
    urlparts = plugin_folder_name.split("/")
    logging.info(f"get_plugin_folder_name: URLParts= {urlparts}")
    if len(urlparts) >1 :
        plugin_folder_name= urlparts[urlpartsindex]
    logging.info(f"plugin_folder_name = {plugin_folder_name}")
    return  plugin_folder_name

# <div class="plugin-detail-content">  <p><a href="https://www.urbancode.com/plugindoc/accurev/">Documentation</a></p>
def extract_tabs(plugin_doc_link):
    doctabs= []
    response=requests.get(plugin_doc_link)
    soup = BeautifulSoup(response.text,SOUP_PARSER)

    alltabs = soup.find_all("a", {"class": "nav-link", "role":"tab"})
    for tab in alltabs:
        logging.debug(f"tab: {tab['href']} and {tab.contents}")
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
            logging.debug(f"sitem: {sitem}")
            plugin_doc_link=sitem['href']
    if plugin_doc_link:
        # extract the doctabs
        logging.debug(f"getdoctabs found {plugin_doc_link} ")
        doctabs = extract_tabs(plugin_doc_link)
    return doctabs
                  
def get_all_plugin_docs(source_url):
    logging.info(f"Plugin URL: {source_url}")

    response = requests.get(source_url)
    soup = BeautifulSoup(response.text, SOUP_PARSER)
    plugin_type = os.getenv("EXPORT_PLUGIN_TYPE")

    allplugindocs = []

    # iterate over all plugin entries (as articles)
    list_of_plugins = soup.find_all("article", class_="uc-grid-item")
    for plugin_item in list_of_plugins:
        if (check_plugin_type(plugin_item, plugin_type)):
            plugin_doc_link = ""
            plugin_doc_link = get_plugin_doc_link(plugin_item)
            logging.info(plugin_doc_link)

            response2 = requests.get(plugin_doc_link)
            oneplugin = {"name": get_plugin_name(response2)}
            oneplugin["plugin_folder_name"]= get_plugin_folder_name(response2)
            oneplugin["doc_folder_name"]= get_doc_folder_name(plugin_doc_link)
            oneplugin["documentation_name"]=""
            oneplugin["doc_tabs"]= get_doc_tabs(response2)
            allplugindocs.append(oneplugin)
    return allplugindocs

def main(argv):
    source_url = os.getenv("PLUGIN_LIST_URL")
    plugin_type = os.getenv("EXPORT_PLUGIN_TYPE")

    allplugindocs = []
    allplugindocs = get_all_plugin_docs(source_url)

    adict = {
        "source_url": source_url,
        "source_overview_url": os.getenv("PLUGIN_OVERVIEW_URL"),
        "source_documentation_url": os.getenv("PLUGIN_DOCUMENTATION_URL"),
        "source_download_folder": os.getenv("PLUGINFILES_SOURCE_URL")
    }

    adict["plugins"] = allplugindocs

    with open (f"{plugin_type}-allplugindocs.json", "w") as f:
        json.dump(adict,f, indent=4)


if __name__ == '__main__':
    main(sys.argv[1:])