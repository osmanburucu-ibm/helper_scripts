import xmltodict
from datetime import datetime
from pathlib import Path
import os, shutil
import logging
import uc_migration_utils as ucutil
import re
import markdownify
from bs4 import BeautifulSoup
from mdutils.mdutils import MdUtils
import csv

script_name = "create_missing_blogs"

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

IMAGE_URL_RE_PNG='href="\/wp-content\/uploads\/.*?\.png"' # '\/wp-content\/uploads\/.*?\.png'# 'href="\/wp-content\/uploads\/.*?\.png"' # 're.findall(r'"(.*?)"', text1))'
IMAGE_URL_RE_JPG='href="\/wp-content\/uploads\/.*?\.jpg"' # 're.findall(r'"(.*?)"', text1))'
IMAGE_URL_RE_SRC_PNG='src="http:\/\/www\.urbancode\.com\/wp-content\/uploads\/.*?\.png"'
IMAGE_URL_RE_SRC_JPG='src="http:\/\/www\.urbancode\.com\/wp-content\/uploads\/.*?\.jpg"'
IMAGE_RE_SRC_PNG='src=\".*?.png\"'
IMAGE_RE_SRC_JPG='src=\".*?.jpg\"'


CAPTION_RE_START='\[caption id=".*?"\]'
CAPTION_RE_END='\[\/caption\]'

# Create shorthand method for conversion
def md(soup, **options):
    return markdownify.MarkdownConverter(**options).convert_soup(soup)

# create directory with TITLE name
# create first text file (title) which contains the original link!
# search for image links, replace them with local file link, copy image from media directory into local dir
# create a html file with the content, name -> Title
# crate a md file with the content, name -> Title
# 

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

def get_publishing_date(ablog):
    
    if ("-" in ablog["pubDate"]):
        d = datetime.strptime(ablog["pubDate"], '%Y-%m-%d %H:%M:%S') 
    else: 
        d = datetime.strptime(ablog["pubDate"], '%a, %d %b %Y %H:%M:%S %z')
    return (d.strftime('%Y.%m.%d'))

def create_dir_and_files(ablog, all_replacable_links):
    config = ucutil.get_config()
    blogs_dir = config[ucutil.BLOGS_DIR]
    
    if ("/" in ablog['title']): sanitized_title=ablog['title'].replace("/", "")
    else: sanitized_title=ablog['title']
  
    targetdir = f"{config[ucutil.BLOGS_DIR]}/migrated/{sanitized_title}"
    ablog_content=ablog['content']
    
    os.makedirs(targetdir, exist_ok=True)
    if not os.path.exists(f"{targetdir}/original_link.txt"):
        with open(f"{targetdir}/original_link.txt", "w") as afile:
            afile.write(ablog['link'])

    ablog_content = process_all_images(blogs_dir, targetdir, ablog_content, IMAGE_URL_RE_PNG)
    ablog_content = process_all_images(blogs_dir, targetdir, ablog_content, IMAGE_RE_SRC_PNG)
    ablog_content = process_all_images(blogs_dir, targetdir, ablog_content, IMAGE_URL_RE_SRC_PNG)    
    ablog_content = process_all_images(blogs_dir, targetdir, ablog_content, IMAGE_URL_RE_JPG)
    ablog_content = process_all_images(blogs_dir, targetdir, ablog_content, IMAGE_RE_SRC_JPG)
    ablog_content = process_all_images(blogs_dir, targetdir, ablog_content, IMAGE_URL_RE_SRC_JPG)  
             
    d = get_publishing_date(ablog)
    
    ablog_content = ucutil.replace_links_in_content(ablog_content, all_replacable_links)
    # TODO: check if URLs in content which are not in my list and add them!!!!
    
    new_content = f"<!DOCTYPE html>\n<html><head><title>{ablog['title']}</title></head>\n<body>\n<p><b>This article was originaly published in {d}</b></p>\n<p><h1>{ablog['title']}</h1></p>\n<p>{ablog_content}\n</p></body>\n</html>\n"
    with open(f"{targetdir}/content.html", "w") as afile:
        afile.write(new_content)
    
    md_doc_file = MdUtils(f"{targetdir}/content.md", title=ablog['title'])
    soup2 = BeautifulSoup(new_content, "html.parser")
   
    md_doc_file.new_paragraph(md(soup2))
    md_doc_file.create_md_file()

def process_all_images(blogs_dir, targetdir, ablogcontent, regex_image_type):
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
        
def create_blog(orig_link, my_dict, all_replacable_links):
    channel = my_dict['rss']['channel']
    ablog = {}
    for i in channel["item"]:
        logger1.info(f"{orig_link} - {i['link']}")
        if (orig_link == i['link']):
            ablog["link"] = i['link']
            ablog["title"] = i['title']
            ablog["pubDate"] = i["pubDate"] or i["wp:post_date"]
            ablog["content"] = i["content:encoded"]
            logger1.info(f"Title={ablog['title']}")
            create_dir_and_files(ablog, all_replacable_links)
    
def main():
    
    config = ucutil.get_config()
    blogs_dir = config[ucutil.BLOGS_DIR]
    
    with open(f"{blogs_dir}/all_content.urbancode.WordPress.xml", "r") as xml_obj:
        my_dict = xmltodict.parse(xml_obj.read())
        xml_obj.close()
        
    all_replacable_links = ucutil.get_list_of_replacable_links()
    all_not_migrated_links = ucutil.get_list_of_not_migrated_links()

    for r in all_not_migrated_links:
        if orig_link := r[0]:
            logger1.info(f"Original-Link={orig_link}")
            create_blog(orig_link, my_dict, all_replacable_links)
            
if __name__ == '__main__':
    main()
