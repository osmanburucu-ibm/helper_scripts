import json
import os
import string
from github import Github
from mdutils.mdutils import MdUtils
import logging
import requests
from bs4 import BeautifulSoup
import markdownify
import uc_migration_utils as ucutil
import re
import base64
import wget

SOUP_PARSER = "lxml" #"html.parser"
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

# Create shorthand method for conversion
def md(soup, **options):
    return markdownify.MarkdownConverter(**options).convert_soup(soup)

def get_list_of_files_from_repo(config):
    all_files = []
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    allfilesname = f'{workfolder}/{config[ucutil.EXPORT_PLUGIN_TYPE]}-all_files.txt'
    if os.path.exists(allfilesname):
        with open(allfilesname, "r") as afile:
            all_files.extend(line[:-1] for line in afile)
    else:
        g = Github(config[ucutil.GITHUB_TOKEN])
        repo = g.get_repo(config[ucutil.GITHUB_TARGET_REPO])
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

def content_to_md_OLD (soupcontent):
    logger1.debug(f"content= {soupcontent}")

    # TODO: download all images into <local repo>/files/images directory and change the reference to this link!
    # TODO: check if reference to urbancode.com or devworks and fix it!
    for item in soupcontent.contents:
        logger1.info(f"item={item}")
     
    contents = "".join(str(item) for item in soupcontent.contents)
    logger1.info(f"contents-original={contents}")
    # the tables are broken no idea why... try to fix it.. does not work well...
    contents = contents.replace("</em></caption>", "</em></caption> <br/>\n <p></p> <br/>\n <p></p>")
    contents = contents.replace("   ", "")
    contents = contents.replace("  ", "") 
    contents = contents.replace("<br/>\n", " ")
    contents = contents.replace("\n </td>", "</td>")  
    contents = contents.replace("\n</td>", "</td>")
    contents = contents.replace("${", "``${")
    contents = contents.replace("}", "}``")
    
    logger1.info(f"content-replaced={contents}")
    soup2 = BeautifulSoup(contents, SOUP_PARSER)
    
    return md(soup2)

def content_to_md (soupcontent):
    logger1.debug(f"content= {soupcontent}")

    # TODO: download all images into <local repo>/files/images directory and change the reference to this link!
    # TODO: check if reference to urbancode.com or devworks and fix it!

    # all_imgs = soupcontent.find_all('img', src=True)
    # for image in all_imgs:
    #       logger1.info(f"image.src={image['src']}")
          
    contents = "".join(str(item) for item in soupcontent.contents)
    logger1.info(f"contents-original={contents}")
    # the tables are broken no idea why... try to fix it.. does not work well...
   # contents = contents.replace("</em></caption>", "</em></caption> <br/>\n <p></p> <br/>\n <p></p>")
    contents = re.sub(r'<caption style=.*</caption>', '', contents)
    
    # contents = contents.replace("   ", "")
    # contents = contents.replace("  ", "") 
    contents = contents.replace("<br/>\n", " ")
    contents = contents.replace("<br/>", " ")    
    #contents = contents.replace(">\n", ">")
    contents = contents.replace("\n </td>", "</td>")  
    contents = contents.replace("\n</td>", "</td>")
    contents = contents.replace("${", "``${")
    contents = contents.replace("}", "}``")
    contents = contents.replace("/wp-content/uploads/plugindocs/", "")
    logger1.info(f"content-replaced={contents}")
    soup2 = BeautifulSoup(contents, SOUP_PARSER)
    
  
    return md(soup2)


def get_latest_version_info(config, plugin):
    versionname = plugin["latestversion"]
    logger1.info(f"Plugin={plugin.get(ucutil.NAME_PLUGIN_NAME)} LatestVersion={versionname}")

    filename = next((file for file in plugin["files"] if (versionname in file)), "")
    logger1.info(f"filename={filename}")

    if filename:     
        all_files = get_list_of_files_from_repo(config)
        target_file_name = next((file for file in all_files if (filename in file)), "")
        logger1.info(f"link={target_file_name}")
        filename = target_file_name

    return versionname, filename

def get_nav_bar(config, plugin, actdoc, doc_level):    
    number_of_columns = 1
    nav_bar_data = ["Back to ..."]
    
    if (doc_level == ucutil.DOC_LEVEL_ALL_PLUGINS):
        # TODO: no nav_bar on top level - check
        return 0, []
   
    if (doc_level == ucutil.DOC_LEVEL_PRODUCT_PLUGINS):
        # TODO: add other products to  nav_bar on Product level - check
        nav_bar_row = ["[All Plugins](../index.md)"]
        
        number_of_columns = len(nav_bar_data)
        nav_bar_data.extend(nav_bar_row)
        return number_of_columns, nav_bar_data
    
    nav_bar_row = ["[All Plugins](../../index.md)"]
    
    nav_bar_data.extend([""])
    nav_bar_row.extend ([f"[{config.get(ucutil.EXPORT_PLUGIN_TYPE)} Plugins](../README.md)"])
    
    if (doc_level == ucutil.DOC_LEVEL_PLUGIN_README):
        nav_bar_data.extend(["Latest Version"])
        plugin_version, plugin_link = get_latest_version_info(config, plugin)
        nav_bar_row.extend([f"[{plugin_version}]({plugin_link})"])

    # nav_bar_row = ["[All Plugins](../../index.md)", "[UCD|UCV|UCR|UCB](../README)", "[PLUGIN.name Readme](README.md)", <list of docs minus act-doc>]
    if (doc_level==ucutil.DOC_LEVEL_PLUGIN_DOCS):
        nav_bar_data.extend([""])
        nav_bar_row.extend ([f"[{plugin.get(ucutil.NAME_PLUGIN_NAME)} Readme](README.md)"])
        
    list_of_docs = get_list_of_doc_tabs(plugin, actdoc)
    
    for docname in list_of_docs:
        nav_bar_data.extend([""])
        nav_bar_row.extend([f"[{docname}]({docname.lower()}.md)"])

    number_of_columns = len(nav_bar_data)
    nav_bar_data.extend(nav_bar_row)
    
    return number_of_columns, nav_bar_data

def get_list_of_doc_tabs(plugin, actdoc):
    list_of_doc_tabs = []

    for doctab in plugin.get(ucutil.NAME_DOC_TABS):
        logger1.info(f"doctabs: {doctab}")
        docname = doctab.get("name", "")
        if (actdoc != docname): list_of_doc_tabs.append(docname)

    # add Downloads tab!
    if (actdoc != ucutil.DOWNLOADS_DOCNAME) and (len(plugin.get(ucutil.NAME_PLUGIN_FILELIST_NAME)) > 0):
        list_of_doc_tabs.append(ucutil.DOWNLOADS_DOCNAME)

    return list_of_doc_tabs

def create_doc_file(docname, soup, config, plugin):
    
    doc_title = f"{plugin[ucutil.NAME_PLUGIN_NAME]} - {docname}"
    target_doc_path = get_target_doc_path(config, plugin)
    doc_file_name = f"{target_doc_path}/{docname.lower()}.md"
    md_doc_file = MdUtils(file_name=doc_file_name, title=doc_title)
    md_doc_file.new_header(level=1, title=docname)
    
    # get content for downloads
    if (docname == ucutil.DOWNLOADS_DOCNAME):
        list_of_plugins_with_link = get_download_list(config, plugin)
        md_doc_file.new_list(list_of_plugins_with_link)
    else:
        doc_content = get_content_for_doc(docname, plugin, soup)
        md_doc_file.new_paragraph(doc_content)
    
    # add nav bar
    number_of_columns, list_of_columns = get_nav_bar(config, plugin, docname, ucutil.DOC_LEVEL_PLUGIN_DOCS)
    md_doc_file.new_table(
        columns=number_of_columns,
        rows=len(list_of_columns) // number_of_columns,
        text=list_of_columns,
        text_align='center',
    )
    
    # create md file
    os.makedirs(target_doc_path, exist_ok=True)
    md_doc_file.create_md_file()

    return doc_file_name 

def create_doc_files(config, plugin):
    list_of_docs = get_list_of_doc_tabs(plugin, "")

    response = requests.get(f"{config[ucutil.PLUGIN_DOCUMENTATION_URL]}/{plugin[ucutil.NAME_DOCUMENTATION_NAME]}")
    soup = BeautifulSoup(response.text, SOUP_PARSER)
    for doc in list_of_docs:
        logger1.debug(f"doc={doc}")
        # create a doc!
        doc_file_name = create_doc_file(doc, soup, config, plugin)
        logger1.info(f"{doc_file_name} created")
    return list_of_docs

def get_content_for_doc(doc, plugin, soup):
    logger1.info(f"doc={doc}")
    doc_not_found = get_doc_not_found(doc)
    md_content = BeautifulSoup(doc_not_found, SOUP_PARSER)
    
    for doctab in plugin.get(ucutil.NAME_DOC_TABS):
        logger1.info(f"doctabs: {doctab}")
        docname = doctab.get("name", "")
        if (doc == docname): 
            tabref = doctab.get("tab_id", "")
            tabarray = tabref.split("#")
            tab_id = tabarray[-1]
            break
    logger1.info(f"tab_id={tab_id}")
    if (tab_id):
        tab = soup.find("div", {"id":tab_id})
        
        download_all_images(doc, plugin, tab)
        
        md_content = content_to_md(tab)
        
    return md_content
    
    # target_doc_path = get_target_doc_path(config, plugin)
    # logger1.info(f"target doc path: {target_doc_path}")
def download_all_images (doc, plugin, soup):
    
    config = ucutil.get_config()
    target_path = get_target_doc_path(config, plugin)
    
    all_imgs = soup.find_all('img')
    for image in all_imgs:
        logger1.info (f"image={image}")
        b64 = False
        if image.has_attr('src'): 
            logger1.info (f"image has src attribute")
            # download image and convert to jpg
            imagepath=f"{target_path}"
            if not os.path.exists(imagepath):
                os.makedirs(imagepath)
            if "http" in image.get("src"):
                lnk = image.get("src")
                
                # TEMPORARY
                #continue
            elif ("base64" in image.get("src")):
                lnk = image['src']
                b64 = True
            else:
                lnk = config.get(ucutil.UC_BASE_URL) + image['src']
                
                # TEMPORARY
                #continue
            if b64:
                logger1.info("src is Base64 image")
            else:
                logger1.info(f"src={lnk}")
            filename = download_image(lnk, imagepath)
            logger1.info (f"filename={filename}")

def download_image(url, imagepath):
    filename = ""
    if "https://www.imwuc.org/media/chbmtcqp.png" in url:
        return "imwuc image not reachable"
    if "base64" in url:
        # decode to image
        return b64_download(url, imagepath)
    try:
    #Get Url
        get = requests.get(url)
        # if the request succeeds
        if get.status_code == 200:
            splitted = url.split("/")
            imagepathname = f"{imagepath}/{splitted[-1]}"
            filename = imagepathname if (os.path.exists(imagepathname)) else wget.download(url, imagepath)
        else:
            filename = "url_image_not_found"
    except requests.exceptions.RequestException as e:
        filename = "url_not_reachable"
    return filename

def b64_download(img_data, imagepath):
    imagenumber = 0
    if "png" in img_data: imgextension = ".png"
    if "jpg" in img_data: imgextension = ".jpg"
    if "jpeg" in img_data: imgextension = ".jpg"
    if "svg" in img_data: imgextension = ".svg"
    #if "pdf" in img_data: imgextension = ".pdf"
    if "gif" in img_data: imgextension = ".gif"
    
    #logger1.info (f"data={img_data}")
    splitted = img_data.split(";base64,")
    logger1.info(f"b64 type={splitted[0]}")
    bimg_data = splitted[-1]
    filename = f"{imagepath}/{imagenumber}{imgextension}"
    while os.path.exists(filename):
        imagenumber += 1
        filename = f"{imagepath}/{imagenumber}{imgextension}"
        
    logger1.info(f"b64: {filename}")    
    bdata = ""
    with open (filename, "wb") as fh:
        bdata = base64.b64decode(bimg_data)
        # base64.decode(bimg_data, bdata)
        fh.write(bdata)
    return filename


def get_file_download_link(config, filename):
    # TODO: change this for VELOCITY special files. some are packed with 7z and splitt, and txt file for info!
    logger1.info(f"Filename={filename}")
    link = ""
    if (filename):
        all_files = get_list_of_files_from_repo(config)
        for file in all_files:
            if (filename in str(file)): link = str(file)
    
    logger1.info("Link={link}")
    return link

def get_download_list(config, plugin):
    items = []
    pluginfiles = plugin.get(ucutil.NAME_PLUGIN_FILELIST_NAME)
    for file in reversed(pluginfiles):
        # get download link for plugin file
        link = get_file_download_link(config, file)
        items.append(f'[{str(file)}]({link})')
    return items 

def create_plugin_landing_page(config, plugin):
    logger1.info (f"Creating landing page for Plug-In {plugin.get(ucutil.NAME_PLUGIN_NAME)}")
    
    target_doc_path = get_target_doc_path(config, plugin)
    logger1.info(f"target doc path: {target_doc_path}")
    
    md_content = get_landing_page_content(config, plugin)
    
    doc_title = f"{plugin[ucutil.NAME_PLUGIN_NAME]}"
    landing_page_md_file_name = f"{target_doc_path}/README.md" # {doc_title}.md  # -> plugin.get(ucutil.NAME_PLUGIN_NAME)
    landing_page_md_file = MdUtils(file_name=landing_page_md_file_name, title=doc_title)            
    landing_page_md_file.new_paragraph(md_content)
    
    number_of_columns, list_of_columns = get_nav_bar(config, plugin, "README", ucutil.DOC_LEVEL_PLUGIN_README)
    landing_page_md_file.new_table(
        columns=number_of_columns,
        rows=len(list_of_columns) // number_of_columns,
        text=list_of_columns,
        text_align='center',
    )    
    
    # TODO: final stage to create file!
    os.makedirs(target_doc_path, exist_ok=True)
    landing_page_md_file.create_md_file()
    return landing_page_md_file_name

def get_landing_page_content(config, plugin):
    # now get content from landing page for plugin if available

    doc_not_found = get_doc_not_found(plugin.get(ucutil.NAME_PLUGIN_NAME))
    landing_page_content = BeautifulSoup(doc_not_found, SOUP_PARSER)
    logger1.debug(f"landing_page_content={landing_page_content}")

    landing_page_doc_name = plugin.get(ucutil.NAME_DOC_FOLDER_NAME)
    if (landing_page_doc_name != ""):
        doc_url = f"{config[ucutil.PLUGIN_OVERVIEW_URL]}/{landing_page_doc_name}"
        logger1.info(f"doc_url={doc_url}")
        response = requests.get(doc_url)
        logger1.debug(f"Response Status Code = {response.status_code}")
        soup = BeautifulSoup(response.text, SOUP_PARSER)
        page_content = soup.find("div", {"id":"container"})
        logger1.debug (f"page_content: {page_content}")
        if (not page_content):
            content = soup.find("main", {"id":"main"})
            page_content = content.find("p")
            logger1.debug (f"again page_content: {page_content}")

        landing_page_content = page_content

    return content_to_md(landing_page_content)

def get_doc_not_found(docname):
    doc_not_found = """<!DOCTYPE html> 
    <html lang="en-US">
        <head>
               <title>DOCNAME</title>
               <meta charset="utf-8">
        </head>
        <body>
            <h2>No Documentation found</h2>
        </body>
    </html>
    """
    doc_not_found = doc_not_found.replace("DOCNAME", docname )
    return doc_not_found

def get_target_doc_path(config, plugin):
    target_doc_folder = plugin.get(ucutil.NAME_PLUGIN_FOLDER_NAME).strip()
    if (not target_doc_folder): target_doc_folder = plugin.get(ucutil.NAME_PLUGIN_NAME).strip()

    return f"{config[ucutil.LOCAL_DOCREPO_LOCATION]}/{config[ucutil.DOC_TARGET_FOLDER]}/{target_doc_folder}"

def main():
    adict = {}

    config = ucutil.get_config()
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]
    
    with open(f'{workfolder}/{config[ucutil.EXPORT_PLUGIN_TYPE]}-all.json', "r") as json_file:
        adict = json.load(json_file)

    for plugin in adict[ucutil.NAME_PLUGIN_LIST_NAME]:
        # create_doc_files(config, plugin, all_files)
        # create only if doc_folder_name is provided
        # DEBUG only accurev-scm to check if download plugins work..
        if (plugin.get(ucutil.NAME_DOC_FOLDER_NAME)): # == "accurev-scm"): 
            landing_page_name = create_plugin_landing_page(config, plugin)
            list_of_docs = create_doc_files(config, plugin)
            logger1.debug(f"landing page={landing_page_name} and docs={list_of_docs} created")

    
    os._exit(0)


if __name__ == '__main__':
    main()