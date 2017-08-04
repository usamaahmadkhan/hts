#!/bin/bash

#This script will build hts project
#usage:
# bash build_hts.sh

. scripts/bash_helpers.sh
. scripts/log_helpers.sh

string=$(sudo cat /proc/version)
if [[ $string == *"Red Hat"* ]]; then
  log "Running build_hts.sh for CentOS"
  bash build_hts_centos.sh
elif [[ $string == *"Ubuntu"* ]]; then
    log "Running build_hts.sh for Ubuntu"
    bash build_hts_ubuntu.sh
  else
    log "Running build_hts.sh for SUSE"
    bash build_hts_suse.sh
fi
