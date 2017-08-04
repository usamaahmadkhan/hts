#!/bin/bash

#This script will cleanup logs and all packages
#usage:
# bash alfred_cleanup.sh

. scripts/bash_helpers.sh
. scripts/log_helpers.sh

log "Removing opt directory"
sudo rm -rf /opt/hts
log "Deleting logs from tmp directory"
sudo rm -rf /tmp/*.tar.gz
log "Removing some packages"
sudo zypper remove qemu
sudo zypper remove libvirt
sudo zypper remove virt-manager
sudo zypper remove nfs-kernel-server
