#!/bin/bash

VMPATH=~/VMs
NEWNAME=cos7k 
BASEVMNAME=COS7.base 
INVENTORYFILE=hosts
GUESTUSER=lnxadm
GUESTPASS=lnxadm
NEWVMIP=

sh createvmclone.sh -n $NEWNAME -b $BASEVMNAME -i $INVENTORYFILE -v $VMPATH -p $GUESTUSER -u $GUESTPASS

#TODO: copy inventory file (hosts) to playbook directory
cp hosts ../deploy-urbancode-deploy 
cp hosts ../deploy-jpetstore-demo 

#TODO: get ip addres to next script

sh addtoknownhosts.sh $NEWVMIP $GUESTUSER $GUESTPASS

cd ../deploy-urbancode-deploy
ansible-playbook setup-all-ucdsa.yml -u $GUESTUSER

cd ../deploy-jpetstore-demo 
ansible-playbook setup-jpetstore-demo.yml -u $GUESTUSER 