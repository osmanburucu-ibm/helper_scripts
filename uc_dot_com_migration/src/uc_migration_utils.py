# sourcery skip: avoid-builtin-shadow
import logging
import os

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
format=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(format)
ch.setFormatter(format)
logger1 = logging.getLogger(__name__)


logger1.addHandler(fh)
logger1.addHandler(ch)


def get_config():
    return {
        "github_api_url": os.getenv("GITHUB_API_URL"),
        "plugin_list_url" : os.getenv("PLUGIN_LIST_URL", "https://www.urbancode.com/plugins"),
        "plugin_type" : os.getenv("EXPORT_PLUGIN_TYPE"), 
        "files_source_url" : os.getenv("PLUGINFILES_SOURCE_URL", "https://www.urbancode.com/uc-downloads/plugins"),
        "plugin_doc_overview_url": os.getenv("PLUGIN_OVERVIEW_URL", "https://www.urbancode.com/plugin"),
        "plugin_full_doc_url": os.getenv("PLUGIN_DOCUMENTATION_URL", "https://www.urbancode.com/plugindoc" ),
        "github_token" : os.getenv("GITHUB_TOKEN"),
        "github_target_repo" : os.getenv("GITHUB_TARGET_REPO"),
        "github_doc_target_repo" : os.getenv("GITHUB_DOC_TARGET_REPO"),
        "github_release_notes_target_repo" : os.getenv("GITHUB_RELEASE_NOTES_TARGET_REPO"),        
        "repo_target_folder" : os.getenv("REPO_TARGET_FOLDER", "files"),
        "doc_target_folder" : os.getenv("DOC_TARGET_FOLDER", "docs"),
        "upload_files_to_repo": os.getenv("UPLOAD_FILES_TO_REPO", "False"),
        "local_repository_location": os.getenv("LOCAL_REPOSITORY_LOCATION", "")
    }

# TODO: x.yyyy also check yyyy ! f.e. 6.86 is higher than 6.111 in this function, should be 6.111 higher!
# TODO: Check that the versionnumber makes sense, as there are several "version naming" conventions used!
def getversionnumber2(elem):
    return float(getversionnumber(elem, True))

def getversionnumber(elem, forsort=False):
    logger1.info(elem)
    split_tup = os.path.splitext(elem)
    logger1.info(split_tup)
    if (":" in str(split_tup[0])):
        parts = split_tup[0].split(":")
    else:
        parts = split_tup[0].split("-")
   #versionnumber = parts[-1] will be used later maybe...
    allnumparts = parts[-1].split(".")
    logger1.info(f"allnumparts={allnumparts}")
    for i in range(len(allnumparts)):
        numfilter = filter(str.isdigit, allnumparts[i])
        numstring = "".join(numfilter)
        if forsort: 
            numstring = numstring.zfill(5)
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
    