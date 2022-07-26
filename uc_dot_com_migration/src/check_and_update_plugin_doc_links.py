import os
import logging
import uc_migration_utils as ucutil

script_name = "check_and_update_plugin_doc_links"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{script_name}.log", "w+")
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
logger1 = logging.getLogger(script_name)


logger1.addHandler(fh)
logger1.addHandler(ch)

def main():
    
    config = ucutil.get_config()
    rootdir=ucutil.get_target_doc_path(config, "", level=ucutil.DOC_LEVEL_PLUGIN_README)
    logger1.debug(f"Rootdir={rootdir}")

    list_of_links=ucutil.get_list_of_not_migrated_links()
    logger1.debug(f"list_of_links={list_of_links}")
    for l in list_of_links:
        link = str(l[0])
        if ("/urbancode/plugin/" in link):
            logger1.info(f"l={link}")
    # for subdir, dirs, files in os.walk(rootdir):
    #     if (rootdir == subdir): continue
    #     logger1.debug (f"subdir={subdir} - dir={dirs}")
    #     logger1.debug (f"files={files}")
    #     update_files_with_new_links(subdir, files, list_of_links)
        
if __name__ == '__main__':
    main()
