# sourcery skip: avoid-builtin-shadow
import logging
import os
from decimal import Decimal
from posixpath import split
from unicodedata import decimal

from pyparsing import nums

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{__name__}.log")
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
        WORKING_FOLDER_LOCATION: os.getenv("WORKING_FOLDER_LOCATION", "exports")
    }

# TODO: x.yyyy also check yyyy ! f.e. 6.86 is higher than 6.111 in this function, should be 6.111 higher!
# TODO: Check that the versionnumber makes sense, as there are several "version naming" conventions used!
def getversionnumber2(elem):
    return Decimal(getversionnumber(elem, True))

def get_allnumparts(elem) -> list:
    split_tup = os.path.splitext(elem.replace("_", "-"))
    logger1.info(split_tup)
    splitchar = ""
    if (":" in str(split_tup[0])):
        splitchar = ":"
    elif ("-" in str(split_tup[0])):
        splitchar = "-"
    else:
        splitchar = "|"

    parts = split_tup[0].split(splitchar)
    logger1.info (f"parts={parts}")
    # if the parts are more than 2 concat from second entry to last with . and create a new allnumparts
    numpartslength = len(parts)
    if numpartslength > 2:
        newstring = ""
        logger1.info(f"len(parts) = {len(parts)}")
        if ("v" in parts[-1]):
            newstring = parts[-1].replace("v", "")
        else:
            if parts[-1].replace(".","").isnumeric():
#                newstring = parts[-1]
#            else:
                for i in range(1, len(parts)):
                    if ("b" in parts[i]): continue
                    if parts[i].replace(".","").isnumeric():
                        logger1.info(f"isnumeric part {parts[i]}")
                        if newstring == "":
                            newstring = parts[i]
                        else:
                            newstring += f".{parts[i]}"
                    logger1.info(f"newstring = {newstring}")
        parts[-1] = newstring
    if parts[-1].replace(".","").isnumeric():
        allnumparts = parts[-1].split(".") if numpartslength >= 2 else ["0"]
    else:
        allnumparts = ["0"]
    
    logger1.info(f"allnumparts={allnumparts}")
    return allnumparts

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

def main():

    print ("Utility Functions for urbancode.com migration project")    
    os._exit(0)

if __name__ == '__main__':
    #main(sys.argv[1:])
    main()
    