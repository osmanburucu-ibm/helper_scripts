import os, sys
from git import Repo
from github import Github
import json
import logging
import uc_migration_utils as ucutil

script_name = "fix_plugin_dir_names"

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

#     target_doc_folder = plugin.get(ucutil.NAME_PLUGIN_FOLDER_NAME).strip()
#    if (not target_doc_folder): target_doc_folder = plugin.get(ucutil.NAME_DOC_FOLDER_NAME).strip()
#    if (not target_doc_folder): target_doc_folder = plugin.get(ucutil.NAME_PLUGIN_NAME).strip()
#
# target_doc_path = get_target_doc_path_from_plugin(config, plugin)

#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def main():
    config = ucutil.get_config()

    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]

    with open(f'{workfolder}/{config[ucutil.EXPORT_PLUGIN_TYPE]}-all.json', "r") as json_file:
        adict = json.load(json_file)    

    allpluginslist = sorted(adict[ucutil.NAME_PLUGIN_LIST_NAME], key=lambda x: x["name"])

    mdfile_name = f'{ucutil.get_target_doc_path(config, "", ucutil.DOC_LEVEL_PLUGIN_README)}/README.md'
    logger1.info(f"mdfile_name={mdfile_name}")
    
    with open(mdfile_name,"rt") as readme_file:
        readme_file_text=readme_file.read()
    for plugin in allpluginslist: # adict[ucutil.NAME_PLUGIN_LIST_NAME]:
        if (plugin.get(ucutil.NAME_DOC_FOLDER_NAME)) and not (plugin.get(ucutil.NAME_PLUGIN_FOLDER_NAME).strip()):
            wrong_name = plugin.get(ucutil.NAME_PLUGIN_NAME).strip().replace("z/", "z")
            wrong_doc_folder_name = ucutil.get_target_doc_path(config, wrong_name)
            logger1.info(f"wrong_name= {wrong_name} - wrong_doc_folder_name={wrong_doc_folder_name}")

            new_name=plugin.get(ucutil.NAME_DOC_FOLDER_NAME).strip()
            new_doc_folder_name = ucutil.get_target_doc_path(config, new_name)
            logger1.info(f"new_name={new_name} - new_doc_folder_name={new_doc_folder_name}")

            # rename folder
            if (os.path.isdir(wrong_doc_folder_name)): 
                os.rename(wrong_doc_folder_name, new_doc_folder_name)
            else:
                if (os.path.isdir(new_doc_folder_name))
                logger1.info(f"directory not found {wrong_doc_folder_name}")
            # replace in README.md in folder from wrong name to new name
            readme_file_text = readme_file_text.replace(f"{wrong_name}/README.md", f"{new_name}/README.md", 1)

    with open(mdfile_name, "wt") as readme_file:
        readme_file.write(readme_file_text)
    os._exit(0)
    
if __name__ == '__main__':
    main()    