#!/bin/bash

# urbancode.com URLs for accessing the plugin files and documentations
# settings for target repositories and repository directory structures

export PLUGIN_LIST_URL="https://www.urbancode.com/plugins"
export PLUGIN_OVERVIEW_URL="https://www.urbancode.com/plugin"
export PLUGIN_DOCUMENTATION_URL="https://www.urbancode.com/plugindoc" 

export DEFAULT_PLUGINFILES_SOURCE_URL="https://www.urbancode.com/uc-downloads/plugins"
export DEFAULT_REPO_TARGET_FOLDER="files"
export DEFAULT_DOC_TARGET_FOLDER="docs"

export EXPORT_PLUGIN_TYPE="" # "Build" | "Deploy" | "Release" | "Velocity"
export PRODUCT_PLUGIN_TYPE="" # "UCB" | "UCD" | "UCR" | "UCD"
export PLUGIN_SOURCE_TYPE="" # "ubuild" | "ibmucd" | "ibmucr" | "ibmucv"

export PLUGINFILES_SOURCE_URL=$DEFAULT_PLUGINFILES_SOURCE_URL"/"$PLUGIN_SOURCE_TYPE
export REPO_TARGET_FOLDER=$DEFAULT_REPO_TARGET_FOLDER"/"$PRODUCT_PLUGIN_TYPE
export DOC_TARGET_FOLDER=$DEFAULT_DOC_TARGET_FOLDER"/"$PRODUCT_PLUGIN_TYPE

export UPLOAD_FILES_TO_REPO="False"
export LOCAL_REPOSITORY_LOCATION=""
export LOCAL_DOCREPO_LOCATION=""

export GITHUB_USERNAME=""
export GITHUB_TOKEN=""
export GITHUB_API_URL="https://api.github.com"
export GITHUB_TARGET_REPO=""