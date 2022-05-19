import json
import os
import sys
import logging
import uc_migration_utils as ucutil

SOUP_PARSER = "html.parser"
script_name = "merge_docs_with_filelist"

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


def get_plugin_docs (pluginfile, localalldocs):
    aplugin = {}
    copyfields = [ucutil.NAME_PLUGIN_NAME, ucutil.NAME_PLUGIN_FOLDER_NAME, ucutil.NAME_DOC_FOLDER_NAME, ucutil.NAME_DOC_TABS, ucutil.NAME_PLUGIN_FILELIST_NAME, ucutil.NAME_PLUGIN_LATESTVERSION_NAME]
    defaultvalues = {
        ucutil.NAME_PLUGIN_FOLDER_NAME:  pluginfile.get(ucutil.NAME_PLUGIN_FOLDER_NAME, ""),
        ucutil.NAME_DOC_FOLDER_NAME:  pluginfile.get(ucutil.NAME_DOC_FOLDER_NAME, ""),
        ucutil.NAME_PLUGIN_FILELIST_NAME: pluginfile.get(ucutil.NAME_PLUGIN_FILELIST_NAME, []),
        ucutil.NAME_PLUGIN_LATESTVERSION_NAME: pluginfile.get(ucutil.NAME_PLUGIN_LATESTVERSION_NAME, "0"),
        ucutil.NAME_DOC_TABS: pluginfile.get(ucutil.NAME_DOC_TABS, []),
        ucutil.NAME_PLUGIN_NAME: pluginfile.get(ucutil.NAME_PLUGIN_FOLDER_NAME, ""),
    }    
    
    aplugin = {
        field: pluginfile.get(field, defaultvalues.get(field))
        for field in copyfields
    }
    for doc_plugin in localalldocs[ucutil.NAME_PLUGIN_LIST_NAME]:
        if (doc_plugin[ucutil.NAME_PLUGIN_FOLDER_NAME] == pluginfile[ucutil.NAME_PLUGIN_FOLDER_NAME]):
            for field in copyfields:
                aplugin[field] = doc_plugin.get(field, defaultvalues.get(field))

    logger1.info(f"aplugin={aplugin}")
        
    return aplugin



def merge_docs_with_plugins(localalldocs, localallplugins):
    copyfields = [ucutil.EXPORT_SOURCE_URL, ucutil.EXPORT_SOURCE_OVERVIEW_URL,
                    ucutil.EXPORT_SOURCE_DOCUMENTATION_URL, ucutil.EXPORT_SOURCE_DOWNLOAD_FOLDER]
    merged = {field: localalldocs[field] for field in copyfields}
    allplugins = []
    for plugin in localallplugins[ucutil.NAME_PLUGIN_LIST_NAME]:
        aplugin = {}
        aplugin = get_plugin_docs (plugin, localalldocs)
        allplugins.append(aplugin)
    
    # if plugins have no pluginfile -> need to add them too!
    for plugin in localalldocs[ucutil.NAME_PLUGIN_LIST_NAME]:
        if (not plugin[ucutil.NAME_PLUGIN_FOLDER_NAME]):
            aplugin = {}
            aplugin = get_plugin_docs (plugin, localallplugins)
            allplugins.append(aplugin)
        
    merged[ucutil.NAME_PLUGIN_LIST_NAME]=allplugins
    return merged

def main():
    
    config = ucutil.get_config()

    plugin_type = config[ucutil.EXPORT_PLUGIN_TYPE] # os.getenv("EXPORT_PLUGIN_TYPE")
    workfolder = config[ucutil.WORKING_FOLDER_LOCATION]

    with open(f"{workfolder}/{plugin_type}-allplugindocs.json", "r") as jdocsin:
        alldocs = json.load(jdocsin)

    with open(f"{workfolder}/{plugin_type}-allplugins.json", "r") as jpluginsin:
        allplugins = json.load(jpluginsin)

    result = merge_docs_with_plugins(alldocs, allplugins)
    with open(f"{workfolder}/{plugin_type}-all.json", "w") as jout:
        json.dump(result, jout, indent=4)


if __name__ == '__main__':
    main()
