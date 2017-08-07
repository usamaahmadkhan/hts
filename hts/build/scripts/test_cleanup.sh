#!/bin/bash

. /root/hts/hts/build/scripts/log_helpers.sh
. /root/hts/hts/build/scripts/bash_helpers.sh
arch=$(uname -m)
log "Cleaning up vms."
for vm in $(sudo virsh -q list | awk '{ print $2 }'); do
  log "Shutting down running vm: $vm"
  sudo virsh destroy $vm
  [[ $? -ne 0 ]] && log "Command to shutdown $vm failed."
  if [ "$arch" == "aarch64" ];then
  sudo virsh undefine --nvram $vm
  else
  sudo virsh undefine $vm
  fi
  [[ $? -ne 0 ]] && log "Command to undefine $vm failed."
done
