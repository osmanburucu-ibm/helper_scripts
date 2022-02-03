# How to use

This is for "cloning" a resource tree from one UCD server to another. It is not very sophisticated (at the moment), and relies that referenced agents and components are available in the target environment!

When time, an better version with more automation (agents, components) will be developed.

## Setup your python environment
install python 3.10 or newer
setup virtualenv if needed
install required libs for the scripts

## First: Set the parameters right

Please copy parameters.example.yml to parameters.yml and edit the values to fit your environment.
In the source and target section set the hostname, port, if you use userid/password use them, if you use an auth token, set userid to PasswordIsAuthToken and token to your token.

## Second: Export the resource tree to a json file

Just execute export_resource_tree using your installed python3.

## Third: Import the resource tree into another UCD Server

Just execute import_resource_tree using your installed python3


## What about the Dockerfile

Working on a containerized version where you do not have to worry about installing python and all the rest. Just pull the container and run it... it is not finished at the moment...
