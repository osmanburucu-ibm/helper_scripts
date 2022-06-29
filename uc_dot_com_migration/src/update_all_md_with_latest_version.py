import os
import logging
import uc_migration_utils as ucutil

script_name = "update_all_md_with_latest_version"

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

def update_latest_version(file_content, latest_version, latest_url):
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
        logger1.debug(f"file_line_item={file_line_item} - number_of_empty_lines={number_of_empty_lines}")
        if (file_line_item == ""): 
            number_of_empty_lines += 1
        else: number_of_empty_lines = 0
        
        if (number_of_empty_lines > 1):
            number_of_empty_lines = 0
            continue
        
        if file_line_index == length_of_file + row_to_split:
            new_line = ucutil.get_new_nav_line(file_line_item, latest_version, latest_url)
        else: new_line = file_line_item
        
        new_file_content = new_file_content + str(new_line) + "\n"
        logger1.debug(f"new_line={new_line} - number_of_empty_lines={number_of_empty_lines}")
        logger1.debug(f"new_file_content={new_file_content} - number_of_empty_lines={number_of_empty_lines}")
    return new_file_content    
    
def update_files_with_latest_version(sub_dir, files):
   
    split_tups = sub_dir.split("/")
    act_dir = split_tups[-1]
   
    latest_version = "0"
    latest_url = ""
    if all_files := ucutil.get_all_files(act_dir):
        all_files.sort(key=ucutil.getversionnumber2)
        latest_version = ucutil.getversionnumber(all_files[-1].split("/")[-1])
        latest_url=all_files[-1]
        logger1.debug(f"latest_version={latest_version} - latest_url={latest_url}")

    for file in files:
        if (".md" not in file): continue
        with open (f"{sub_dir}/{file}", "r") as f:
            file_content = f.readlines()
        
        # copy the first 6 lines which contain the header and the last 3 lines with updated latest version!
        new_content = update_latest_version(file_content, latest_version, latest_url)
        logger1.debug(f"new_content={''.join(new_content)}")
        with open (f"{sub_dir}/{file}", "w") as f_out:
            rval = f_out.write ("".join(new_content))
            logger1.debug (f"rval from f_out.write={rval}")

 
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

    for subdir, dirs, files in os.walk(rootdir):
        if (rootdir == subdir): continue
        logger1.debug (f"subdir={subdir} - dir={dirs}")
        logger1.debug (f"files={files}")
        update_files_with_latest_version(subdir, files)
        
if __name__ == '__main__':
    main()
