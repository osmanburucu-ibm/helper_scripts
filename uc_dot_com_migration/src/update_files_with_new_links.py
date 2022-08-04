import os
import logging
import uc_migration_utils as ucutil

script_name = "update_files_with_new_links"

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

def update_files_with_new_links(sub_dir, files, list_of_links):
    config = ucutil.get_config()
    DRY_RUN= config[ucutil.DEBUG_DRY_RUN]

    for file in files:
        if (".md" not in file) and (".html" not in file):
            continue
        logger1.info (f"{sub_dir}/{file}")
        with open (f"{sub_dir}/{file}", "r") as f:
            file_content = f.readlines()

        new_content = ''.join(file_content)
        for url_list in list_of_links:
            logger1.debug(f"url_list={url_list}")
            logger1.debug(f"url_list[URL_ORIGINAL_LINK]={url_list[ucutil.URL_ORIGINAL_LINK]} - url_list[ucutil.URL_NEW_LINK]={url_list[ucutil.URL_NEW_LINK]}")
            new_content = new_content.replace(url_list[ucutil.URL_ORIGINAL_LINK], url_list[ucutil.URL_NEW_LINK])
        if (new_content != ''.join(file_content)):
            logger1.debug(f"new_content={''.join(new_content)}")
            if (DRY_RUN == "True"):
                rval = "DRY_RUN"
            else:
                with open (f"{sub_dir}/{file}", "w") as f_out:
                    rval = f_out.write ("".join(new_content))
            logger1.info (f"rval from f_out.write={rval}")
 
def main():
    
    config = ucutil.get_config()
    rootdir= config[ucutil.DOCS_DIR]
    logger1.debug(f"Rootdir={rootdir}")

    list_of_links=ucutil.get_list_of_replacable_links()
    logger1.debug(f"list_of_links={list_of_links}")
    for subdir, dirs, files in os.walk(rootdir):
        if (rootdir == subdir): continue
        logger1.debug (f"subdir={subdir} - dir={dirs}")
        logger1.debug (f"files={files}")
        update_files_with_new_links(subdir, files, list_of_links)
        
if __name__ == '__main__':
    main()
