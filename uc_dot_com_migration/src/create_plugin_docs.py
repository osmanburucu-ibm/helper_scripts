import json
import os
from github import Github
from mdutils.mdutils import MdUtils
import logging
import requests
from bs4 import BeautifulSoup
import markdownify
import uc_migration_utils as ucutil


SOUP_PARSER = "html.parser"
script_name = "create_plugin_docs"

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

# Create shorthand method for conversion
def md(soup, **options):
    return markdownify.MarkdownConverter(**options).convert_soup(soup)

def get_list_of_files_from_repo(config, repo):
    all_files = []
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    allfilesname = f'{workfolder}/{config[ucutil.EXPORT_PLUGIN_TYPE]}-all_files.txt'
    if os.path.exists(allfilesname):
        with open(allfilesname, "r") as afile:
            all_files.extend(line[:-1] for line in afile)
    else:
        contents = repo.get_contents("")
        with open(allfilesname, "w") as afile:
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    logger1.info(f"ALL_FILES={file_content} - {file_content.path} - {file_content.download_url} -  {file_content.size} - {file_content.url}")
                    all_files.append(str(file_content.download_url))
                    afile.write(str(file_content.download_url))
                    afile.write("\n")
            #afile.writelines(all_files)
    return all_files

def content_to_md (soupcontent):
    logger1.info(f"content= {soupcontent}")

    contents = "".join(str(item) for item in soupcontent.contents)
    # the tables are broken no idea why... try to fix it.. does not work well...
    contents = contents.replace("</em></caption>", "</em></caption> \n <p></p> \n <p></p>")
    contents = contents.replace("   ", "")
    contents = contents.replace("  ", "") 
    contents = contents.replace(" \n", " ")
    contents = contents.replace("\n </td>", "</td>")  
    contents = contents.replace("\n</td>", "</td>")
    contents = contents.replace("${", "``${")
    contents = contents.replace("}", "}``")
    
    soup2 = BeautifulSoup(contents, SOUP_PARSER)
    
    return md(soup2)

def get_content_for_doc(config, plugin):
    mdcontent = ""
    response = requests.get(f"{config[ucutil.PLUGIN_DOCUMENTATION_URL]}/{plugin[ucutil.NAME_DOC_FOLDER_NAME]}")

    soup = BeautifulSoup(response.text, SOUP_PARSER)

    mdcontent = content_to_md(soup)
    logger1.info(f"mdcontent = {mdcontent}")
    
    return mdcontent

def create_doc_files(config, plugin, all_files):
    logger1.info(f"create doc for plugin: {plugin}")
    plugin_doc_name = plugin.get(ucutil.NAME_DOC_FOLDER_NAME)
    if (plugin_doc_name == ""): plugin_doc_name = plugin.get(ucutil.NAME_PLUGIN_NAME)
    
    plugin_folder_name = plugin.get(ucutil.NAME_PLUGIN_FOLDER_NAME)
    if plugin_folder_name == "": plugin_folder_name = plugin_doc_name
    
    doc_path = f"{config[ucutil.LOCAL_DOCREPO_LOCATION]}/{config[ucutil.DOC_TARGET_FOLDER]}/{config[ucutil.DOC_PLUGIN_TYPE]}/{plugin_folder_name}"
    doc_name = f"{doc_path}/{plugin_doc_name}_Documentation.md"
    logger1.info (f"doc_name = {doc_name}")
    
    doc_title = f"{plugin[ucutil.NAME_PLUGIN_NAME]} - Documentation"

    doc_md_file = MdUtils(file_name=doc_name, title=doc_title)
  
    if (plugin.get(ucutil.NAME_DOC_FOLDER_NAME) != ""):
        doc_url = f"{config[ucutil.PLUGIN_DOCUMENTATION_URL]}/{plugin_doc_name}"
        logger1.info(f"doc_url={doc_url}")
        response = requests.get(doc_url)
        logger1.info(f"Response Status Code = {response.status_code}")
        soup = BeautifulSoup(response.text, SOUP_PARSER)
        # check response code
        # response.status_code
        for doctab in plugin[ucutil.NAME_DOC_TABS]:
            logger1.info(f"doctabs: {doctab}")
            doc_md_file.new_header(level=1, title=doctab[ucutil.NAME_DOC_TABS_NAME])
            tabref = doctab.get(ucutil.NAME_DOC_TABS_ID, "")
            tabarray = tabref.split("#")
            tab_id = tabarray[-1]
            tab_content = soup.find("div", {"id":tab_id})
            md_tab_content = content_to_md(tab_content)
            doc_md_file.new_paragraph(md_tab_content)
        logger1.info(f"doc_md_file={doc_md_file}")
    
    # create directory if needed
    os.makedirs(doc_path, exist_ok=True)
    doc_md_file.create_md_file()

def main():
    adict = {}

    config = ucutil.get_config()
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    
    with open(f'{workfolder}/{config[ucutil.EXPORT_PLUGIN_TYPE]}-all.json', "r") as json_file:
        adict = json.load(json_file)
    
    g = Github(config[ucutil.GITHUB_TOKEN])
    repo = g.get_repo(config[ucutil.GITHUB_TARGET_REPO])
    
    all_files = get_list_of_files_from_repo(config, repo)
    
    for plugin in adict[ucutil.NAME_PLUGIN_LIST_NAME]:
        create_doc_files(config, plugin, all_files)

    
    os._exit(0)


if __name__ == '__main__':
    main()