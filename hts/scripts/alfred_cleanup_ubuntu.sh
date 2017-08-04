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
sudo apt-get purge qemu-system-arm -y
sudo apt-get purge qemu-efi -y
sudo apt-get purge libvirt-bin -y
sudo apt-get purge virt-manager -y
sudo apt-get purge nfs-kernel-server -y
