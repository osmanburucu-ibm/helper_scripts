# sourcery skip: avoid-builtin-shadow
import logging
import os
from decimal import Decimal
from posixpath import split
from unicodedata import decimal
from github import Github
import json
import csv
import re
from pathlib import Path
import shutil
from pyparsing import nums

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{__name__}.log", 'w+')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
logger1 = logging.getLogger(__name__)


logger1.addHandler(fh)
logger1.addHandler(ch)

GITHUB_API_URL = "github_api_url"
PLUGIN_LIST_URL = "plugin_list_url"
EXPORT_PLUGIN_TYPE = "plugin_type"
DOC_PLUGIN_TYPE = "doc_plugin_type"
PLUGINFILES_SOURCE_URL = "files_source_url"
PLUGIN_OVERVIEW_URL = "plugin_doc_overview_url"
PLUGIN_DOCUMENTATION_URL = "plugin_full_doc_url"
GITHUB_TOKEN = "github_token"
GITHUB_TARGET_REPO = "github_target_repo"
GITHUB_DOC_TARGET_REPO = "github_doc_target_repo"
GITHUB_RELEASE_NOTES_TARGET_REPO = "github_release_notes_target_repo"
REPO_TARGET_FOLDER = "repo_target_folder"
DOC_TARGET_FOLDER = "doc_target_folder"
UPLOAD_FILES_TO_REPO = "upload_files_to_repo"
LOCAL_REPOSITORY_LOCATION = "local_repository_location"
WORKING_FOLDER_LOCATION="working_folder"
LOCAL_DOCREPO_LOCATION = "local_docrepo_location"

EXPORT_SOURCE_URL = "source_url"
EXPORT_SOURCE_OVERVIEW_URL = "source_overview_url"
EXPORT_SOURCE_DOCUMENTATION_URL = "source_documentation_url"
EXPORT_SOURCE_DOWNLOAD_FOLDER = "source_download_folder"

NAME_PLUGIN_LIST_NAME = "plugins"
NAME_PLUGIN_NAME = "name"
NAME_PLUGIN_FOLDER_NAME = "plugin_folder_name"
NAME_PLUGIN_LATESTVERSION_NAME = "latestversion"
NAME_PLUGIN_FILELIST_NAME = "files"
NAME_DOC_FOLDER_NAME = "doc_folder_name"
NAME_DOCUMENTATION_NAME = "documentation_name"
NAME_DOC_TABS = "doc_tabs"
NAME_DOC_TABS_NAME = "name"
NAME_DOC_TABS_ID = "tab_id"

MARKDOWN_EXTENSION = "md"

DOWNLOADS_DOCNAME = "Downloads"

DOC_LEVEL_PLUGIN_DOCS= "DOC_LEVEL_PLUGIN_DOCS"
DOC_LEVEL_PLUGIN_README= "DOC_LEVEL_PLUGIN_README"
DOC_LEVEL_PRODUCT_PLUGINS="DOC_LEVEL_PRODUCT_PLUGINS"
DOC_LEVEL_ALL_PLUGINS="DOC_LEVEL_ALL_PLUGINS"

UC_BASE_URL="UC_BASE_URL"

DEFAULT_DOC_TARGET_FOLDER="DEFAULT_DOC_TARGET_FOLDER"

RECREATE_DOC_FILES="RECREATE_DOC_FILES"
RECREATE_PLUGIN_DOC_FILE="RECREATE_PLUGIN_DOC_FILE"
RECREATE_PRODUCT_INDEX_FILE="RECREATE_PRODUCT_INDEX_FILE"
SKIP_DOC_FILES="SKIP_DOC_FILES"

EXPORTED_ALL_WP_CONTENT_FILE="EXPORTED_ALL_WP_CONTENT_FILE"
EXPORTED_DOCS_PATH="EXPORTED_DOCS_PATH"
EXPORTED_ALL_PLUGINS_LIST="EXPORTED_ALL_PLUGINS_LIST"
EXPORTED_PLUGIN_DOCS="EXPORTED_PLUGIN_DOCS"

PRODUCT_PLUGIN_TYPE="PRODUCT_PLUGIN_TYPE"

BLOGS_DIR="BLOGS_DIR"
BLOGS_FILE_NAME="BLOGS_FILE_NAME"

URL_ORIGINAL_LINK="URL_ORIGINAL_LINK"
URL_NEW_LINK="URL_NEW_LINK"
URL_NEW_YES="URL_NEW_YES"

# URLS_WITH_REPLACEMENTS.csv
ALL_URLS_LIST_FILE_NAME="ALL_URLS_LIST_FILE_NAME"

DEBUG_DRY_RUN="DEBUG_DRY_RUN"

RELEASE_NOTES_DIR_FILE_NAME="RELEASE_NOTES_DIR_FILE_NAME"
RELEASE_NOTES_DIR="RELEASE_NOTES_DIR"


IMAGE_URL_RE_PNG='href="\/wp-content\/uploads\/.*?\.png"' # '\/wp-content\/uploads\/.*?\.png'# 'href="\/wp-content\/uploads\/.*?\.png"' # 're.findall(r'"(.*?)"', text1))'
IMAGE_URL_RE_JPG='href="\/wp-content\/uploads\/.*?\.jpg"' # 're.findall(r'"(.*?)"', text1))'
IMAGE_URL_RE_SRC_PNG='src="http:\/\/www\.urbancode\.com\/wp-content\/uploads\/.*?\.png"'
IMAGE_URL_RE_SRC_JPG='src="http:\/\/www\.urbancode\.com\/wp-content\/uploads\/.*?\.jpg"'
IMAGE_RE_SRC_PNG='src=\".*?.png\"'
IMAGE_RE_SRC_JPG='src=\".*?.jpg\"'



def get_config():
    return {
        GITHUB_API_URL: os.getenv("GITHUB_API_URL", "https://api.github.com"),
        PLUGIN_LIST_URL: os.getenv("PLUGIN_LIST_URL", "https://www.urbancode.com/plugins"),
        UC_BASE_URL: os.getenv("UC_BASE_URL", "http://www.urbancode.com"), 
        EXPORT_PLUGIN_TYPE: os.getenv("EXPORT_PLUGIN_TYPE"),
        DOC_PLUGIN_TYPE: os.getenv("DOC_PLUGIN_TYPE"),
        PLUGINFILES_SOURCE_URL: os.getenv("PLUGINFILES_SOURCE_URL", "https://www.urbancode.com/uc-downloads/plugins"),
        PLUGIN_OVERVIEW_URL: os.getenv("PLUGIN_OVERVIEW_URL", "https://www.urbancode.com/plugin"),
        PLUGIN_DOCUMENTATION_URL: os.getenv("PLUGIN_DOCUMENTATION_URL", "https://www.urbancode.com/plugindoc" ),
        GITHUB_TOKEN: os.getenv("GITHUB_TOKEN"),
        GITHUB_TARGET_REPO: os.getenv("GITHUB_TARGET_REPO"),
        GITHUB_DOC_TARGET_REPO: os.getenv("GITHUB_DOC_TARGET_REPO"),
        GITHUB_RELEASE_NOTES_TARGET_REPO: os.getenv("GITHUB_RELEASE_NOTES_TARGET_REPO"),        
        REPO_TARGET_FOLDER: os.getenv("REPO_TARGET_FOLDER", "files"),
        DEFAULT_DOC_TARGET_FOLDER: os.getenv("DEFAULT_DOC_TARGET_FOLDER", "docs"),        
        DOC_TARGET_FOLDER: os.getenv("DOC_TARGET_FOLDER", DEFAULT_DOC_TARGET_FOLDER),
        UPLOAD_FILES_TO_REPO: os.getenv("UPLOAD_FILES_TO_REPO", "False"),
        LOCAL_REPOSITORY_LOCATION: os.getenv("LOCAL_REPOSITORY_LOCATION", ""),
        LOCAL_DOCREPO_LOCATION: os.getenv("LOCAL_DOCREPO_LOCATION"),
        WORKING_FOLDER_LOCATION: os.getenv("WORKING_FOLDER_LOCATION", "exports"),
        RECREATE_DOC_FILES: os.getenv(RECREATE_DOC_FILES, "True"),
        RECREATE_PLUGIN_DOC_FILE: os.getenv(RECREATE_PLUGIN_DOC_FILE, "True"),
        RECREATE_PRODUCT_INDEX_FILE: os.getenv(RECREATE_PRODUCT_INDEX_FILE, "True"),
        SKIP_DOC_FILES: os.getenv(SKIP_DOC_FILES, "False"),
        EXPORTED_ALL_WP_CONTENT_FILE: os.getenv(EXPORTED_ALL_WP_CONTENT_FILE,"all_content.urbancode.WordPress.xml"),
        EXPORTED_DOCS_PATH: os.getenv(EXPORTED_DOCS_PATH, "exports/WP_exports"),
        EXPORTED_ALL_PLUGINS_LIST: os.getenv(EXPORTED_ALL_PLUGINS_LIST, "plugins.urbancode.WordPress.xml"),
        EXPORTED_PLUGIN_DOCS: os.getenv(EXPORTED_PLUGIN_DOCS, "plugin-docs.urbancode.WordPress.xml"),
        PRODUCT_PLUGIN_TYPE:os.getenv(PRODUCT_PLUGIN_TYPE, ""),
        DEBUG_DRY_RUN:os.getenv(DEBUG_DRY_RUN, "False"),
        ALL_URLS_LIST_FILE_NAME:os.getenv(ALL_URLS_LIST_FILE_NAME,"URLS_WITH_REPLACEMENTS.csv"),
        BLOGS_DIR:os.getenv(BLOGS_DIR,"~/Rnd/Blogs"),
        BLOGS_FILE_NAME:os.getenv(BLOGS_FILE_NAME, "MERGED-all_urls.xlsx"),
        RELEASE_NOTES_DIR:os.getenv(BLOGS_DIR,"~/Rnd/Release_Notes"),
        RELEASE_NOTES_DIR_FILE_NAME:os.getenv(RELEASE_NOTES_DIR_FILE_NAME, "RELEASE_NOTES_DIR.csv")
    }

def get_all_plugins_list(all_plugins_list):
    if (len(all_plugins_list) == 0):
        adict = {}
        config = get_config()
        workfolder = config[WORKING_FOLDER_LOCATION]

        with open(f'{workfolder}/{config[EXPORT_PLUGIN_TYPE]}-all.json', "r") as json_file:
            adict = json.load(json_file)

        all_plugins_list = sorted(adict[NAME_PLUGIN_LIST_NAME], key=lambda x: x["name"])
    return all_plugins_list

def get_list_of_files_from_repo(config):
    all_files = []
    workfolder = config[WORKING_FOLDER_LOCATION]
    allfilesname = f'{workfolder}/{config[EXPORT_PLUGIN_TYPE]}-all_files.txt'
    if os.path.exists(allfilesname):
        with open(allfilesname, "r") as afile:
            all_files.extend(line[:-1] for line in afile)
    else:
        g = Github(config[GITHUB_TOKEN])
        repo = g.get_repo(config[GITHUB_TARGET_REPO])
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

# TODO: x.yyyy also check yyyy ! f.e. 6.86 is higher than 6.111 in this function, should be 6.111 higher!
# TODO: Check that the versionnumber makes sense, as there are several "version naming" conventions used!
def getversionnumber2(elem):
    return Decimal(getversionnumber(elem, True))

def get_allnumparts(elem) -> list:

    if ("http" in elem): 
        split_tup = elem.split("/")
        new_elem = split_tup[-1]
    else: new_elem = elem
    new_elem = new_elem.replace("_", "-")
    if (".tar.zip" in new_elem):
        split_tup = new_elem.split(".tar.zip")
    elif (".tar.7z" in new_elem):
        split_tup = new_elem.split(".tar.7z")
    else: split_tup = os.path.splitext(new_elem)
    logger1.info(split_tup)
    splitchar = get_split_char(split_tup)

    parts = split_tup[0].split(splitchar)
    logger1.info (f"parts={parts}")
    numpartslength = len(parts)
    if numpartslength > 2:
        newstring = ""
        logger1.info(f"len(parts) = {len(parts)}")
        if ("v" in parts[-1]):
            newstring = parts[-1].replace("v", "")
        elif parts[-1].replace(".","").isnumeric():
            newstring = get_versionnumber_parts(parts)
        parts[-1] = newstring
    if parts[-1].replace(".","").isnumeric():
        allnumparts = parts[-1].split(".") if numpartslength >= 2 else ["0"]
    else:
        allnumparts = ["0"]

    logger1.info(f"allnumparts={allnumparts}")
    return allnumparts

def get_versionnumber_parts(parts, newstring=""):
    for i in range(1, len(parts)):
        if ("b" in parts[i]): continue
        if parts[i].replace(".","").isnumeric():
            logger1.info(f"isnumeric part {parts[i]}")
            if newstring == "":
                newstring = parts[i]
            else:
                newstring += f".{parts[i]}"
        logger1.info(f"newstring = {newstring}")
    return newstring

def get_split_char(split_tup):
    if (":" in str(split_tup[0])):
        return ":"
    elif "-" in str(split_tup[0]):
        return "-"
    else:
        return "|"

def getversionnumber(elem, forsort=False):
    logger1.info(elem)
    allnumparts = get_allnumparts(elem)
    for i in range(len(allnumparts)):
        logger1.info(f"itearating over allnumparts= {allnumparts[i]}")
        numfilter = filter(str.isdigit, allnumparts[i])
        numstring = "".join(numfilter)
        logger1.info(f"numstring after filter = {numstring}")
        if forsort:
            filllenghth = 8 # len(numstring) + 2
            numstring = numstring.zfill(filllenghth)
        allnumparts[i] = "".join(numstring)

    x = "0"
    if allnumparts[0].isnumeric():
        x = f'{allnumparts[0]}.' if forsort else f'{allnumparts[0]}'
        for i in range(1, len(allnumparts)):
            x = x + allnumparts[i] if forsort else f"{x}.{allnumparts[i]}"
    logger1.info(x)
    return x

def get_target_doc_path(config, target_doc_folder, level=DOC_LEVEL_PLUGIN_DOCS):
    
    target_doc_path = f"{config[LOCAL_DOCREPO_LOCATION]}/{config[DEFAULT_DOC_TARGET_FOLDER]}"
    if level==DOC_LEVEL_ALL_PLUGINS: return target_doc_path
    
    target_doc_path = f"{config[LOCAL_DOCREPO_LOCATION]}/{config[DOC_TARGET_FOLDER]}"
    if level == DOC_LEVEL_PLUGIN_README: return target_doc_path 
    
    if (level == DOC_LEVEL_PLUGIN_DOCS) and (target_doc_folder):
        target_doc_path = f"{target_doc_path}/{target_doc_folder}"
        
    return target_doc_path

def get_new_nav_line(file_line_item, latest_version, latest_url):
    last_line_splitted=file_line_item.split("|")
    logger1.info(f"last_line_splitted={last_line_splitted}")
    new_last_line="|"
    for index, item in enumerate(last_line_splitted):
        if (item in ["","\n"]): continue
        new_item = f"[{latest_version}]({latest_url})" if (index == 3) else f"{item}"
        new_last_line = new_last_line + str(new_item) + "|"
    logger1.info(f"new_last_line={new_last_line}")
    return new_last_line

def extract_abstract(read_lines):
    lines = read_lines[5:10]
    doubleemptyline=0
    newlines = []
    for idx in range(len(lines)):
        logger1.info(f"line={lines[idx].strip()}")
        if (lines[idx].strip() == ""):
            if (idx > 0) : 
                doubleemptyline = doubleemptyline +1
                logger1.info(f"doubleemptyline={doubleemptyline}")
            continue
        # ignore table lines
        if lines[idx][0] in ["|", "*"]: continue
        if ("---" in lines[idx].strip()) or ("===" in lines[idx].strip()): continue
        if ("Available Steps" in lines[idx].strip()) or ("**Platform Support**" in lines[idx].strip()): 
            return " ".join(newlines).strip()
        newlines.append(lines[idx])
    return " ".join(newlines).strip()

def get_latest_version_info(config, plugin):
    versionname = plugin["latestversion"]
    logger1.info(f"Plugin={plugin.get(NAME_PLUGIN_NAME)} LatestVersion={versionname}")

    filename = next((file for file in plugin["files"] if (versionname in file)), "")
    logger1.info(f"filename={filename}")

    if filename:     
        all_files = get_list_of_files_from_repo(config)
        target_file_name = next((file for file in all_files if (filename in file)), "")
        logger1.info(f"link={target_file_name}")
        filename = target_file_name

    return versionname, filename

def get_target_doc_path_from_plugin(config, plugin, level=DOC_LEVEL_PLUGIN_DOCS):
    target_doc_folder = plugin.get(NAME_PLUGIN_FOLDER_NAME).strip()
    if (not target_doc_folder): target_doc_folder = plugin.get(NAME_DOC_FOLDER_NAME).strip()
    if (not target_doc_folder): target_doc_folder = plugin.get(NAME_PLUGIN_NAME).strip()
    
    if (level == DOC_LEVEL_PRODUCT_PLUGINS): return target_doc_folder
    
    return get_target_doc_path(config, target_doc_folder, level)

def get_list_of_doc_tabs(plugin, actdoc):
    list_of_doc_tabs = []

    for doctab in plugin.get(NAME_DOC_TABS):
        logger1.info(f"doctabs: {doctab}")
        docname = doctab.get("name", "")
        if (actdoc != docname): list_of_doc_tabs.append(docname)

    # add Downloads tab!
    if (actdoc != DOWNLOADS_DOCNAME) and (len(plugin.get(NAME_PLUGIN_FILELIST_NAME)) > 0):
        list_of_doc_tabs.append(DOWNLOADS_DOCNAME)

    return list_of_doc_tabs

def get_all_files(act_dir):
    config = get_config()
    all_files = get_list_of_files_from_repo(config)
    search_string=f"/main/files/{act_dir}/"
    return [str(file) for file in all_files if (search_string in str(file))]

def get_nav_bar(config, plugin, actdoc, doc_level, act_dir=""):    
    if (doc_level == DOC_LEVEL_ALL_PLUGINS):
        # TODO: no nav_bar on top level - check
        return 0, []

    nav_bar_data = ["Back to ...", ""]
    if (doc_level == DOC_LEVEL_PRODUCT_PLUGINS):
        nav_bar_data.append(f"{plugin.get(NAME_PLUGIN_NAME)} ")
        nav_bar_row = ["[All Plugins](../index.md)", "[Top](#contents)", f"[Readme]({get_target_doc_path_from_plugin(config, plugin, doc_level)}/README.md)"]
    else:
        nav_bar_row = ["[All Plugins](../../index.md)", f"[{config.get(EXPORT_PLUGIN_TYPE)} Plugins](../README.md)"]

    nav_bar_data.append("Latest Version")
    if (act_dir)and (all_files := get_all_files(act_dir)):
            all_files.sort(key=getversionnumber2)
            plugin_version = getversionnumber(all_files[-1].split("/")[-1])
            plugin_link=all_files[-1]
    else:
        plugin_version, plugin_link = get_latest_version_info(config, plugin)
    nav_bar_row.append(f"[{plugin_version}]({plugin_link})")

    if (doc_level==DOC_LEVEL_PLUGIN_DOCS):
        nav_bar_data.append(f"{plugin.get(NAME_PLUGIN_NAME)} ")
        nav_bar_row.append("[Readme](README.md)")

    if doc_level in [DOC_LEVEL_PLUGIN_DOCS, DOC_LEVEL_PLUGIN_README]:
        list_of_docs = get_list_of_doc_tabs(plugin, actdoc)
        for docname in list_of_docs:
            nav_bar_data.append("")
            nav_bar_row.append(f"[{docname}]({docname.lower()}.md)")

    number_of_columns = 1
    number_of_columns = len(nav_bar_data)
    logger1.info(f"number_of_columns={number_of_columns} - nav_bar_rows={nav_bar_data} - nav_bar_rows={nav_bar_row} size={len(nav_bar_row)}")
    nav_bar_data.extend(nav_bar_row)
    logger1.info(f"number_of_columns={number_of_columns} - nav_bar={nav_bar_data} size={len(nav_bar_data)}")

    return number_of_columns, nav_bar_data

# URLS_WITH_REPLACEMENTS
def get_list_of_urls_with_replacements(filter_field, filter_value, which_url):
    config = get_config()
    blogs_dir = config[BLOGS_DIR]
    list_of_urls_file_name=config[ALL_URLS_LIST_FILE_NAME]
    
    list_of_replacable_links=[]
    # load CSV with its path
    with open(f"{blogs_dir}/{list_of_urls_file_name}",  encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=";")
        list_of_rows=list(reader)
    
    for r in list_of_rows:
        if r[filter_field].lower()==filter_value:
            logger1.debug(f"r={r}")
            entry=[r[0], r[which_url]]
            list_of_replacable_links.append(entry)
    return list_of_replacable_links

def get_list_of_replacable_links():
    return get_list_of_urls_with_replacements(2, "yes", 3)
def get_list_of_not_migrated_links():
    return get_list_of_urls_with_replacements(2, "", 1)

def copy_image_to_target(targetdir, image_name, blogs_dir, image_path):
    new_image_name = image_name
    logger1.debug(f"first new_image_name={new_image_name}")
    if not os.path.exists(f"{targetdir}/{new_image_name}"):
        if os.path.exists(f"{blogs_dir}/media/{image_path}/{new_image_name}"): 
            shutil.copyfile(f"{blogs_dir}/media/{image_path}/{new_image_name}", f"{targetdir}/{new_image_name}")
        else: 
            logger1.debug(f"image not found {new_image_name}")
            if x := re.search("(-\d+?x\d+?\.png)", new_image_name):
                logger1.debug(f"image regex found {new_image_name}")
                isplit = new_image_name.split(x[0])
                iextension=Path(new_image_name).suffix
                new_image_name=f"{isplit[0]}{iextension}"
                logger1.debug(f"new new_image_name={new_image_name}")
                copy_image_to_target(targetdir, new_image_name, blogs_dir, image_path)
    return new_image_name

def process_all_images(blogs_dir, targetdir, ablogcontent, regex_image_type):
    CAPTION_RE_START='\[caption id=".*?"\]'
    CAPTION_RE_END='\[\/caption\]'

    ablog_content = ablogcontent
    logger1.debug(f"regex_imagetype={regex_image_type}")
    all_images=[]
    r = re.findall(rf"{regex_image_type}", ablog_content) 

    all_images.extend(r)
    logger1.debug(f"r={r}")
    for ir in all_images:
        image_with_path=ir.strip()
        image_with_path=image_with_path.replace('http://www.urbancode.com', '')
        image_with_path=image_with_path.replace('href=', '')
        image_with_path=image_with_path.replace('src=', '')
        image_with_path=image_with_path.replace('"', '')
        logger1.debug(f"image link={image_with_path}")
        splitted = image_with_path.split("/")
        logger1.debug(f"{splitted}")
        image_name = splitted[-1]

        logger1.debug(f"Target={targetdir}/{image_name}")
        image_path = Path(image_with_path).parent.absolute()
        logger1.debug(f"image_path={image_path}")
        ablog_content = ablog_content.replace(f"{str(image_path)}/", "")
        ablog_content = re.sub(CAPTION_RE_START, "\n", ablog_content, flags=re.MULTILINE)
        ablog_content = ablog_content.replace(CAPTION_RE_END, "\n") # re.sub(CAPTION_RE_END, "\n", ablog_content, flags=re.MULTILINE)
       
        new_image_name = copy_image_to_target(targetdir, image_name, blogs_dir, image_path)               
        if (new_image_name != image_name):
            ablog_content=ablog_content.replace(image_name, new_image_name)
    return ablog_content

def replace_links_in_content (content, all_replacable_links):
    
    new_content = content
    for l in all_replacable_links:
        logger1.debug(f"l={l}")
        if l:        
            new_content = new_content.replace(l[0], l[1])
    return new_content

def main():

    print ("Utility Functions for urbancode.com migration project")    
    os._exit(0)

if __name__ == '__main__':
    #main(sys.argv[1:])
    main()
    