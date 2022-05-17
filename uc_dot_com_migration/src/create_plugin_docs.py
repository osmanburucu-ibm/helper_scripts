import json
import os
from github import Github
import sys
import logging
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


def main():
    adict = {}

    config = ucutil.get_config()
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    
    with open(f'{workfolder}/{config[ucutil.EXPORT_PLUGIN_TYPE]}-all.json', "r") as json_file:
        adict = json.load(json_file)
    
    g = Github(config[ucutil.GITHUB_TOKEN])
    repo = g.get_repo(config[ucutil.GITHUB_TARGET_REPO])
    
    all_files = get_list_of_files_from_repo(config, repo)
    
    os._exit(0)


if __name__ == '__main__':
    main()