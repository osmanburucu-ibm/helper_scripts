#!/bin/sh
VMPATH="$1"
NEWNAME="$2"
BASEVMNAME="$3"

[ -z "$1" ] && VMPATH="~/VMs"
[ -z "$2" ] && NEWNAME="cloned-image"
[ -z "$3" ] && BASEVMNAME="COS77.base.vmwarevm"


echo "$VMPATH"
echo "$NEWNAME"
echo "$BASEVMNAME"
echo "$BASEVMPATH"