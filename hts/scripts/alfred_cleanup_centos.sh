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
sudo yum remove AAVMF qemu-img qemu-kvm qemu -y
sudo yum remove libvirt libvirt-python libvirt-client virt-install virt-viewer bridge-utils -y
sudo yum remove virt-manager -y
sudo yum remove nfs-utils -y
