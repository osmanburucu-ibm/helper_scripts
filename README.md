# helper_scripts
simple scripts for my other projects

## Scripts

### createvmclone

~~~sh

sh createvmclone.sh <vmpath> <newname> <basevmname> <ansible inventory file with path>

~~~

prereqs: vmware tools have to be installed in the base image!

this script will clone a given base image and will insiert its name and ip address to an ansible inventory file
