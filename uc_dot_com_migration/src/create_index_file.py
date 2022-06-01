import markdown
import os
from mdutils.mdutils import MdUtils
import logging
import uc_migration_utils as ucutil

SOUP_PARSER = "lxml" #"html.parser"
script_name = "create_index_file"

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



def get_name_and_content_from_md(pluginpath):
    with open(f"{pluginpath}", "r") as f:
        plugin_content = f.read().split("\n")
    name_index = 1 if (plugin_content[0] == "") else 0
    return plugin_content[name_index].strip(), plugin_content

def get_plugin(plugin_name, plugindir, global_allpluginslist):
    global_allpluginslist = ucutil.get_all_plugins_list(global_allpluginslist)
        
    found_plugin = {}

    for pl in global_allpluginslist:
        #logger1.info(f"{pl.get(ucutil.NAME_PLUGIN_NAME)}")
        if (pl.get(ucutil.NAME_PLUGIN_NAME).strip() == plugin_name):
            logger1.info(f"pluginname found = {plugin_name}")
            found_plugin=pl
            break
        if (pl.get(ucutil.NAME_PLUGIN_FOLDER_NAME).strip() == plugindir):
            logger1.info(f"plugindir found = {plugindir}")
            found_plugin=pl
            break
        if (pl.get(ucutil.NAME_DOC_FOLDER_NAME).strip() == plugindir):
            logger1.info(f"plugindir found = {plugindir}")
            found_plugin=pl
            break
        
    return found_plugin

def main():
    global_allpluginslist = []
    config = ucutil.get_config()
    logger1.debug(f"config={config}")
    
    mdfile_name = ucutil.get_target_doc_path(config, "", ucutil.DOC_LEVEL_PLUGIN_README)
    prod_index_mdfile = MdUtils(file_name=f'{mdfile_name}/README',title=f'Welcome to UrbanCode {config[ucutil.EXPORT_PLUGIN_TYPE]} Plugins')
    prod_index_mdfile.new_header(level=1, title='List of all Plugins')  # style is set 'atx' format by default. 
    
    rootdir=ucutil.get_target_doc_path(config, "", level=ucutil.DOC_LEVEL_PLUGIN_README)
    logger1.info(f"Rootdir={rootdir}")
    alldirs=os.listdir(rootdir)
    alldirs.sort()
    logger1.info(f"alldirs={alldirs}")
    for plugindir in alldirs:
        logger1.info(f"plugindir={plugindir}")
        if os.path.isdir(f"{rootdir}/{plugindir}"):
            plugin_name, plugin_content = get_name_and_content_from_md(f"{rootdir}/{plugindir}/README.md")
            logger1.info(f"Name={plugin_name} - Content={plugin_content}")
            plugin = get_plugin (plugin_name, plugindir, global_allpluginslist)
            logger1.info(f"plugin={plugin}")
            prod_index_mdfile.new_header(level=2, title=f"{plugin_name}")
        
            plugin_abstract = ucutil.extract_abstract(plugin_content)
            prod_index_mdfile.new_paragraph(plugin_abstract)
            prod_index_mdfile.new_paragraph("---\n  ")
            number_of_columns, list_of_columns = ucutil.get_nav_bar(config, plugin, "README", ucutil.DOC_LEVEL_PRODUCT_PLUGINS)
            prod_index_mdfile.new_table(
                columns=number_of_columns,
                rows=len(list_of_columns) // number_of_columns,
                text=list_of_columns,
                text_align='center',
            )
              
    prod_index_mdfile.new_table_of_contents(table_title='Contents', depth=2)
    prod_index_mdfile.create_md_file()
    os._exit(0)


if __name__ == '__main__':
    main()