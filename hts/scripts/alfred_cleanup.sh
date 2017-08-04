#!/bin/bash

#This script will cleanup logs and all packages
#usage:
# bash alfred_cleanup.sh

. scripts/bash_helpers.sh
. scripts/log_helpers.sh

string=$(sudo cat /proc/version)
if [[ $string == *"Red Hat"* ]]; then
  log "Running alfred_cleanup.sh for CentOS"
  bash scripts/alfred_cleanup_centos.sh
elif [[ $string == *"Ubuntu"* ]]; then
  log "Running alfred_cleanup.sh for Ubuntu"
  bash scripts/alfred_cleanup_ubuntu.sh
  else
      log "Running alfred_cleanup.sh for SuSE"
      bash scripts/alfred_cleanup_suse.sh
fi
