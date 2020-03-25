#!/bin/bash
# this shell script will clone the given vmware fusion image with the new name
# createvmclone <vmpath> <newname> <basevmname> <ansible inventory file with path>
VMPATH="$1"
NEWNAME="$2"
BASEVMNAME="$3"
INVENTORYFILE="$4"

[ -z "$1" ] && VMPATH="~/VMs"
[ -z "$2" ] && NEWNAME="cloned-image"
[ -z "$3" ] && BASEVMNAME="COS77.base"
[ -z "$4" ] && INVENTORYFILE="../hosts"


BASEVMPATH="${BASEVMNAME}.vmwarevm"

echo "using VMPATH=${VMPATH} NEWNAME=${NEWNAME} BASEVMNAME=${BASEVMNAME} BASEVMPATH=${BASEVMPATH} INVENTORYFILE=${INVENTORYFILE}"

echo "will clone from base image"
vmrun clone "${VMPATH}/${BASEVMPATH}/${BASEVMNAME}.vmx" "${VMPATH}/$NEWNAME.vmwarevm/$NEWNAME.vmx" full -cloneName=$NEWNAME

echo "will start cloned image"
vmrun start "${VMPATH}/$NEWNAME.vmwarevm/$NEWNAME.vmx"
echo "need to wait till it is up"
tstate=`vmrun checkToolsState "${VMPATH}/$NEWNAME.vmwarevm/$NEWNAME.vmx"`
until [ $tstate = "running" ]
do 
    echo "checking state ..."
    sleep 20
    tstate=`vmrun checkToolsState "${VMPATH}/$NEWNAME.vmwarevm/$NEWNAME.vmx"`
done
echo "state of vmtools = $tstate"

echo "waiting for network to come up and get ip address..."
ipaddresse=`vmrun getGuestIPAddress "${VMPATH}/$NEWNAME.vmwarevm/$NEWNAME.vmx"`
until [[ $ipaddresse != *"Error"* ]]
do 
    echo "checking ip address ..."
    sleep 20
    ipaddresse=`vmrun getGuestIPAddress "${VMPATH}/$NEWNAME.vmwarevm/$NEWNAME.vmx"`
done
echo "ip address of vm is $ipaddresse"

echo "preparing inventory file for ansible"
echo "[ucd_server]" > "$INVENTORYFILE"
echo "$NEWNAME.local.net ansible_host=$ipaddresse" >> "$INVENTORYFILE"
echo " " >> "$INVENTORYFILE"
echo "[db_server]" >> "$INVENTORYFILE"
echo "$NEWNAME.local.net ansible_host=$ipaddresse" >> "$INVENTORYFILE"
echo "DONE"