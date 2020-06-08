# helper_scripts

A collection of scripts.

## VMWare Automation Scripts

Simple scripts for my other projects, createvmclone is based on [Virtjunkie.com repo](https://github.com/jonhowe/Virtjunkie.com)

Cannot remember where i had found the base for addtoknownhosts.

Both scripts were tested only on Mac OS (zsh) so they could work on Linux but not sure.

### createvmclone

This script will clone a given base image and will insert its name and ip address to an ansible inventory file

~~~sh

sh ./createvmclone -v|--vms <path to vmware image directory> -n|--name <New VM name> -b|--base <Template/Base VM name> -i|--inventory <Ansible inventory file>

~~~

The parameters -u|--user and -p|--pass are not used, but are the admin user for the vm image with its password

pre-reqs: vmware tools have to be installed in the base image!


### addtoknownhosts

This script will exchange your ssh keys with the image for the given userid (must exist in the image) so that no password will be asked during execution of the playbooks. The password will be asked during the run of this shell script.

~~~sh

sh ./addtoknownhosts.sh <ip address of running image> <userid for image>

~~~

## Upgrading / Updating UrbanCode

### upgrade_ucd_agent.py

This script will iterate over all IBM UrbanCode Agents and upgrade the ones with a given tag.
