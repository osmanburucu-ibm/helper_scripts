#!/bin/bash

./set_env.sh $1 $2

# DEBUG uncomment later
export RECREATE_PRODUCT_INDEX_FILE="False"
export RECREATE_PLUGIN_DOC_FILE="False"
export RECREATE_DOC_FILES="False"
export SKIP_DOC_FILES="True"

case $2 in
    "DUMP-PLUGINS")
        python3 src/dump_all_plugins.py
        ;;
    "DUMP-DOCS")
        python3 src/dump_all_plugin_docs.py
        ;;
    "MERGE")
        python3 src/merge_docs_with_fileslist.py
        ;;
    "CREATE-DOCS")
        python3 src/create_plugin_docs.py
        ;;
    "DO-DUMP-DOCS-MERGE")
        python3 src/dump_all_plugin_docs.py
        python3 src/merge_docs_with_fileslist.py
        ;;
    "DO-MERGE-CREATE")
        python3 src/merge_docs_with_fileslist.py
        python3 src/create_plugin_docs.py
        ;;
    "DO-DUMP-DOCS-CREATE")
        python3 src/dump_all_plugin_docs.py
        python3 src/merge_docs_with_fileslist.py
        python3 src/create_plugin_docs.py
        ;;
    "DO-ALL")
        python3 src/dump_all_plugins.py
        python3 src/dump_all_plugin_docs.py
        python3 src/merge_docs_with_fileslist.py
        python3 src/create_plugin_docs.py
        ;;
    *)
        echo "not a valid argument"
        echo
        ;;
esac
