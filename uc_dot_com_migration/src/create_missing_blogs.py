import xmltodict
from datetime import datetime
import openpyxl
import os
import logging
import uc_migration_utils as ucutil

script_name = "create_missing_blogs"

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

# create directory with TITLE name
# create first text file (title) which contains the original link!
# search for image links, replace them with local file link, copy image from media directory into local dir
# create a html file with the content, name -> Title
# crate a md file with the content, name -> Title
# 

def get_publishing_date(ablog):
    
    d = datetime.strptime(ablog["pubDate"], '%a, %d %b %Y %H:%M:%S %z')
    return (d.strftime('%Y.%m.%d'))
def create_dir_and_files(ablog):
    config = ucutil.get_config()
    targetdir = f"{config[ucutil.BLOGS_DIR]}/migrated/{ablog['title']}"
    os.makedirs(targetdir, exist_ok=True)
    with open(f"{targetdir}/original_link.txt", "w") as afile:
        afile.write(ablog['link'])
    d = get_publishing_date(ablog)
    new_content = f"<!DOCTYPE html>\n<html><head><title>{ablog['title']}</title></head>\n<body>\n<p>This article was originaly published in {d}</p>\n{ablog['content']}\n</body>\n</html>\n"
    with open(f"{targetdir}/content.html", "w") as afile:
        afile.write(new_content)
    
def create_blog(orig_link, my_dict):
    channel = my_dict['rss']['channel']
    ablog = {}
    for i in channel["item"]:
        if (orig_link == i['link']):
            ablog["link"] = i['link']
            ablog["title"] = i['title']
            ablog["pubDate"]=i["pubDate"]
            ablog["content"]=i["content:encoded"]
            logger1.info(f"Title={ablog['title']}")
            create_dir_and_files(ablog)
            
def main():
    
    config = ucutil.get_config()
    blogs_dir = config[ucutil.BLOGS_DIR]
    with open(f"{blogs_dir}/all_content.urbancode.WordPress.xml", "r") as xml_obj:
        my_dict = xmltodict.parse(xml_obj.read())
        xml_obj.close()

    # load excel with its path
    wrkbk = openpyxl.load_workbook(f"{blogs_dir}/MERGED-all_urls.xlsx")
    sh = wrkbk.active
    
    # iterate through excel and display data
    for i in range(2, sh.max_row+1):
        print("\n")
        print("Row ", i, " data :")
        orig_link=""
        for j in range(1, sh.max_column+1):
            cell_obj = sh.cell(row=i, column=j)
            print (f"{cell_obj.value} - ")
            if j==1: orig_link=cell_obj.value
            if ("urbancode" not in orig_link) or (j==2 and cell_obj.value=="YES") or (j==3 and cell_obj.value!=None) or ("www.urbancode.com/plugin" in orig_link):
                orig_link=""
                break
                
        if orig_link: 
            logger1.info(f"Original-Link={orig_link}")
            create_blog(orig_link, my_dict)
            
if __name__ == '__main__':
    main()
