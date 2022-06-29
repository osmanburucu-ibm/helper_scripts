import json
import os
import sys
import logging
import uc_migration_utils as ucutil

script_name = "update_downloadslist"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{script_name}.log", "w+")
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

def get_list_of_versions(all_files):
    new_lines = ""
    for item in reversed (all_files):
        if ("EPL.txt" in item): continue
        filename_splitted=item.split("/")
        new_lines = f"{new_lines}- [{filename_splitted[-1]}]({str(item)})\n"
    return new_lines

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

def update_latest_version(file_content, latest_version, latest_url, all_files):
    # last line needs to get new latest version if different
    row_to_split = -1
    if (file_content[row_to_split] == "\n"): row_to_split = -2
    logger1.debug(f"row to change={file_content[row_to_split]}")
    
    new_file_content = ""
    length_of_file=len(file_content)
    logger1.debug(f"length_of_file={length_of_file}")
    number_of_empty_lines = 0
    for file_line_index, line_item in enumerate(file_content):
        file_line_item = line_item.strip()
        logger1.info(f"file_line_item={file_line_item} - number_of_empty_lines={number_of_empty_lines}")
        if (file_line_item == ""): 
            number_of_empty_lines += 1
        elif (file_line_item[0] == "-"):
            continue
        else: number_of_empty_lines = 0
        
        if (number_of_empty_lines > 1):
            number_of_empty_lines = 0
            continue
        
        if ("|Back to" in file_line_item):
            # now add all new files in reverse order
            new_line = get_list_of_versions(all_files) + "\n" + file_line_item
        else: new_line = file_line_item
        
        if file_line_index == length_of_file + row_to_split:
            new_line = get_new_nav_line(file_line_item, latest_version, latest_url)
        new_file_content = new_file_content + str(new_line) + "\n"
        logger1.info(f"new_line={new_line} - number_of_empty_lines={number_of_empty_lines}")
        logger1.info(f"new_file_content={new_file_content} - number_of_empty_lines={number_of_empty_lines}")
        
    return new_file_content
    

def update_downloads_list(sub_dir, act_dir):
    if not os.path.exists(f"{sub_dir}/downloads.md"): return
    
    if all_files := ucutil.get_all_files(act_dir):
        all_files.sort(key=ucutil.getversionnumber2)
        latest_version = ucutil.getversionnumber(all_files[-1].split("/")[-1])
        latest_url=all_files[-1]
        logger1.info(f"all_files={all_files} - latest_version={latest_version}")
        with open (f"{sub_dir}/downloads.md", "r") as f:
            downloads_file = f.readlines()
        
        logger1.debug(f"downloads_file={downloads_file}")
        # copy the first 6 lines which contain the header and the last 3 lines with updated latest version!
        new_content = update_latest_version(downloads_file, latest_version, latest_url, all_files)
        logger1.info(f"new_content={''.join(new_content)}")
        with open (f"{sub_dir}/downloads.md", "w") as f_out:
            rval = f_out.write ("".join(new_content))
            logger1.info (f"rval from f_out.write={rval}")
    else:
        logger1.warning(f"Plugin Doc {act_dir} folder needs to be mapped to Plugin Folder")

    
def main():
    
    config = ucutil.get_config()

    product_name=config[ucutil.PRODUCT_PLUGIN_TYPE]
    logger1.debug(f"product_name={product_name}")
    
    plugin_type = config[ucutil.EXPORT_PLUGIN_TYPE] 
    logger1.debug(f"plugin_type={plugin_type}")
    
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    logger1.debug(f"workfolder={workfolder}")
    
    rootdir=ucutil.get_target_doc_path(config, "", level=ucutil.DOC_LEVEL_PLUGIN_README)
    logger1.debug(f"Rootdir={rootdir}")
    all_dirs = []
    for subdir, dirs, files in os.walk(rootdir):
        logger1.debug (f"subdir={subdir} - dir={dirs}")
        splitted_dirs = subdir.split(rootdir)
        if splitted_dirs[-1]:
            logger1.debug(f"splitted_dirs={splitted_dirs[-1]}")
            act_dir=str(splitted_dirs[-1])[1:]
            all_dirs.append(act_dir)
            update_downloads_list(subdir, act_dir)
#        for file in files:
#            # Debug

  #  logger1.info(f"all_dirs={all_dirs}")

if __name__ == '__main__':
    main()
