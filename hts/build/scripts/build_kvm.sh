#!/bin/bash

#This script will configure/install all tools/packages/dependencies required to
#execute Thunder-KVM test plan
#usage:
# bash build_kvm.sh

. /root/hts/build/scripts/bash_helpers.sh
. /root/hts/build/scripts/log_helpers.sh

export LC_ALL=C
string=$(sudo cat /proc/version)
if [[ $string == *"Red Hat"* ]]; then
  log "Running build_kvm.sh for CentOS"
  bash /root/hts/build/scripts/build_kvm_centos.sh
elif [[ $string == *"Ubuntu"* ]]; then
  log "Running build_kvm.sh for Ubuntu"
  bash /root/hts/build/scripts/build_kvm_ubuntu.sh
  else
      log "Running build_kvm.sh for SUSE"
      bash /root/hts/build/scripts/build_kvm_suse.sh
fi
