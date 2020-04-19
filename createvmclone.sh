#!/bin/bash
# this shell script will clone the given vmware fusion image with the new name
# createvmclone -v|--vms <path to vmware image directory> -n|--name <New VM name> -b|--base <Template/Base VM name> -i|--inventory <Ansible inventory file>
# -u|--user and -p|--pass are not used, but are the admin user for the vm image with its password
VMPATH=
NEWNAME=
BASEVMNAME=
INVENTORYFILE=
GUESTUSER=
GUESTPASS=
VMWARETYPE=fusion


echo "Parameters are:"
while true; do
    case $1 in 
        -u | --user )
            GUESTUSER=$2; echo "User=$GUESTUSER"; shift 2 ;;
        -p | --pass )
            GUESTPASS=$2; echo "Pass=$GUESTPASS"; shift 2 ;;
        -v | --vms )
            VMPATH=$2; echo "VMs locations=$VMPATH"; shift 2 ;;            
        -n | --name )
            NEWNAME=$2; echo "New VM-Name=$NEWNAME"; shift 2 ;;
        -b | --base )
            BASEVMNAME=$2; echo "Base VM-Name=$BASEVMNAME"; shift 2 ;;
        -i | --inventory )
            INVENTORYFILE=$2; echo "Inventoryfile=$INVENTORYFILE"; shift 2 ;;
        -- ) echo "-- $1"; shift; break ;;
        * ) break ;;
    esac
done
echo

clone_vm() {
    BASEVMPATH="${BASEVMNAME}"
    if [ $VMWARETYPE == "fusion" ]; then
        BASEVMPATH="${BASEVMPATH}.vmwarevm"
    fi

    SOURCE="${VMPATH}/${BASEVMPATH}/${BASEVMNAME}.vmx"
    NEWVM="${VMPATH}/$NEWNAME"
    if [ $VMWARETYPE == "fusion" ]; then
        NEWVM="${NEWVM}.vmwarevm"
    fi
    NEWVM="${NEWVM}/$NEWNAME.vmx"

    echo "CLONING: $BASEVMNAME to $NEWNAME"
# vmrun -T fusion -gu $GUESTUSER -gp $GUESTPASS  ........
    vmrun  clone $SOURCE $NEWVM full -cloneName=$NEWNAME 

    echo "STARTING: $NEWVM"
    vmrun start $NEWVM

    echo "WAITING: .. starting .. vmtools .."
    until (vmrun  checkToolsState $NEWVM | grep -q "running"); do 
        printf '.'
        sleep 5;
    done
    sleep 10
    echo

    echo "WAITING: .. vm-ip .. "
    until (vmrun  getGuestIPAddress $NEWVM | grep -q -v "Error: Unable to get the IP address"); do
        printf "."
        sleep 5
    done
    sleep 10
    echo

    IP="$(vmrun  getGuestIPAddress $NEWVM)"
    echo "VM is running and has the IP Address: $IP"
    echo

    echo "INVENTORYFILE: preparing inventory file for ansible"
    echo "[ucd_server]" > "$INVENTORYFILE"
    echo "$NEWNAME.local.net ansible_host=$IP" >> "$INVENTORYFILE"
    echo " " >> "$INVENTORYFILE"
    echo "[db_server]" >> "$INVENTORYFILE"
    echo "$NEWNAME.local.net ansible_host=$IP" >> "$INVENTORYFILE"
    echo
    echo "DONE"
}
clone_vm $VMPATH $NEWNAME $BASEVMNAME $INVENTORYFILE $GUESTUSER $GUESTPASS
