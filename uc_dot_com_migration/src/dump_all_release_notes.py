import logging
from datetime import datetime
import xmltodict
import uc_migration_utils as ucutil
import os
from bs4 import BeautifulSoup
from mdutils.mdutils import MdUtils
import markdownify

script_name = "dump_all_release_notes"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{script_name}.log", "w+")
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
logger1 = logging.getLogger(script_name)

logger1.addHandler(fh)
logger1.addHandler(ch)


# Create shorthand method for conversion
def md(soup, **options):
    return markdownify.MarkdownConverter(**options).convert_soup(soup)

# all_content.urbancode.WordPress.xml

def get_all_release_notes(all_content):
    
    allreleasenotes=[]
    channel = all_content['rss']['channel']
    for i in channel["item"]:
        arn = {}
        if (i["wp:post_type"] == "release_note"):
            arn["link"] = i['link']
            arn["title"] = i['title']
            arn["pubDate"] = i["pubDate"] or i["wp:post_date"]
            if ("-" in arn["pubDate"]):
                d = datetime.strptime(arn["pubDate"], '%Y-%m-%d %H:%M:%S') 
            else: 
                d = datetime.strptime(arn["pubDate"], '%a, %d %b %Y %H:%M:%S %z')
            arn["pubDate"] = d.strftime('%Y.%m.%d')

            arn["content"] = i["content:encoded"]
            arn["product"] = "unknown"
            arn["version"] = "unknown"
            logger1.debug(f"link={arn['link']}") 
            for p in i["wp:postmeta"]:
                if (isinstance(p, str)): continue
                k = list(p.items())[0]
                if k[1] == "related_products":
                    x = list(p.items())[1]
                    if x[1] == 'a:1:{i:0;s:2:"95";}': arn["product"] = "UCB"
                    if x[1] == 'a:1:{i:0;s:2:"96";}': arn["product"] = "UCD"
                    if x[1] == 'a:1:{i:0;s:2:"97";}': arn["product"] = "UCR"
                    if x[1] == 'a:1:{i:0;s:2:"811";}': arn["product"] = "UCV"
                    if x[1] == 'a:1:{i:0;s:3:"811";}': arn["product"] = "UCV"
                if k[1] == "version":
                    x = list(p.items())[1]
                    arn["version"] = x[1]
            logger1.debug(f"Title={arn['title']} - Version={arn['version']} - Product={arn['product']} - link={arn['link']}")
            if arn["version"] !="unknown": allreleasenotes.append(arn) 
    return allreleasenotes

def create_dir_and_files(arn, all_replacable_links):
    config = ucutil.get_config()
    blogs_dir = config[ucutil.BLOGS_DIR]
    version_name=arn["version"]

    version_name = version_name.replace("/", "") if ("/" in version_name) else version_name

    targetdir = f"{config[ucutil.BLOGS_DIR]}/{arn['product']}/{version_name}"
    arn_content=arn['content']

    os.makedirs(targetdir, exist_ok=True)
    with open(f"{targetdir}/original_link.txt", "a") as afile:
        afile.write(f"{arn['link']}\n")

    arn_content = ucutil.process_all_images(blogs_dir, targetdir, arn_content, ucutil.IMAGE_URL_RE_PNG)
    arn_content = ucutil.process_all_images(blogs_dir, targetdir, arn_content, ucutil.IMAGE_RE_SRC_PNG)
    arn_content = ucutil.process_all_images(blogs_dir, targetdir, arn_content, ucutil.IMAGE_URL_RE_SRC_PNG)
    arn_content = ucutil.process_all_images(blogs_dir, targetdir, arn_content, ucutil.IMAGE_URL_RE_JPG)
    arn_content = ucutil.process_all_images(blogs_dir, targetdir, arn_content, ucutil.IMAGE_RE_SRC_JPG)
    arn_content = ucutil.process_all_images(blogs_dir, targetdir, arn_content, ucutil.IMAGE_URL_RE_SRC_JPG)  

    d = arn['pubDate']
    arn_content = ucutil.replace_links_in_content(arn_content, all_replacable_links)
    new_content = f"<!DOCTYPE html>\n<html><head><title>{arn['version']}</title></head>\n<body>\n<p><b>This article was originaly published in {d}</b></p>\n<p><h1>{arn['title']}</h1></p>\n<p>{arn_content}\n</p></body>\n</html>\n"
    with open(f"{targetdir}/{arn['title']}.html", "w") as afile:
        afile.write(new_content)

    md_doc_file = MdUtils(f"{targetdir}/{arn['title']}.md") #, title=ablog['title'])
    soup2 = BeautifulSoup(new_content, "html.parser")

    md_doc_file.new_paragraph(md(soup2))
    md_doc_file.create_md_file()

def main():
    
    config = ucutil.get_config()
    blogs_dir = config[ucutil.BLOGS_DIR]
    content_file=config[ucutil.EXPORTED_ALL_WP_CONTENT_FILE]
    
    with open(f"{blogs_dir}/{content_file}", "r") as xml_obj:
        my_dict = xmltodict.parse(xml_obj.read())
        xml_obj.close()
    
    all_replacable_links = ucutil.get_list_of_replacable_links()
    allreleasenotes = get_all_release_notes(my_dict)
    allreleasenotes = sorted(allreleasenotes, key=lambda k: (k['product'], k['version'], k['pubDate']))
    for rn in allreleasenotes:
        logger1.info(f"Title={rn['title']} - Version={rn['version']} - Product={rn['product']} - link={rn['link']}")
        create_dir_and_files(rn, all_replacable_links)

if __name__ == '__main__':
    # main(sys.argv[1:])
    main()