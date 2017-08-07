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
sudo zypper remove -y qemu
sudo zypper remove -y virt-manager
sudo zypper remove -y nfs-kernel-server
log "Removing repos"
sudo zypper removerepo http://download.opensuse.org/repositories/Virtualization/SLE_12/ repo-virt
sudo zypper removerepo http://download.opensuse.org/repositories/benchmark/SLE_12_SP2_Backports/ repo-backport
sudo zypper removerepo http://download.opensuse.org/repositories/Base:System/openSUSE_Factory_zSystems/ repo-base
sudo zypper removerepo http://download.opensuse.org/repositories/network/SLE_12_SP3/ repo-network
sudo zypper removerepo http://download.opensuse.org/repositories/network:/utilities/SLE_12_SP3/ repo-netutils
sudo zypper removerepo http://download.opensuse.org/tumbleweed/repo/oss repo-tmblwd
