#!/bin/bash
#This script will configure/install LTP required to
#execute Thunder-KVM test plan
#usage:
# bash install_ltp.sh

. /root/hts/hts/build/scripts/bash_helpers.sh
. /root/hts/hts/build/scripts/log_helpers.sh

string=$(sudo cat /proc/version)
if [[ $string == *"Red Hat"* ]]; then
  log "Running install_ltp.sh for CentOS"
  bash /root/hts/hts/build/scripts/install_ltp_centos.sh
elif [[ $string == *"Ubuntu"* ]]; then
  log "Running install_ltp.sh for Ubuntu"
  bash /root/hts/hts/build/scripts/install_ltp_ubuntu.sh
  else
      log "Running install_ltp.sh for Suse"
      bash /root/hts/hts/build/scripts/install_ltp_suse.sh
fi
