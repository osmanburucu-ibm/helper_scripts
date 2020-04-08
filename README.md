# helper_scripts
simple scripts for my other projects, based on [Virtjunkie.com repo](https://github.com/jonhowe/Virtjunkie.com)

## Scripts

### createvmclone

~~~sh

sh createvmclone -v|--vms <path to vmware image directory> -n|--name <New VM name> -b|--base <Template/Base VM name> -i|--inventory <Ansible inventory file>

~~~

The parameters -u|--user and -p|--pass are not used, but are the admin user for the vm image with its password

prereqs: vmware tools have to be installed in the base image!

this script will clone a given base image and will insiert its name and ip address to an ansible inventory file
