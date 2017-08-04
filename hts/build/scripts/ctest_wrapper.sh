#!/bin/bash

. /root/hts/build/scripts/bash_helpers.sh
. /root/hts/build/scripts/log_helpers.sh
path=/root/hts/build/scripts

function cleanup () {
arch=$(uname -m)
log "Cleaning up vms."
for vm in $(sudo virsh -q list --all | awk '{ print $2 }'); do
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
  bridge=/sys/class/net/br0/operstate
  if [ -e "$bridge" ]
  then
    sudo ip link set br0 down
    sudo brctl delbr br0
  fi
}

#### main code ####
# check parameters
if [[ $# -lt 3 ]]; then
  log "Not enough parameters provided: $#"
  exit 1
fi

# otherwise, fill our parameters and run the test
CTEST_TEST_TIMEOUT="$1"
CTEST_TEST_BINARY_DIR="$2"
CTEST_TEST_NAME="$3"
shift 3
log "Starting test in traditional mode: name='${CTEST_TEST_NAME}' dir='${CTEST_TEST_BINARY_DIR}' timeout='${CTEST_TEST_TIMEOUT}'"
log "Running commandline: $@"
sudo /usr/bin/timeout -k 2 ${CTEST_TEST_TIMEOUT} $@
status=$?
log "Test returned status: $status"

# If the test above timed out, it did not have any chance to collect
# logs. Since this wrapper, unlike pita_wrapper, does not include
# test_helpers, logs are not collected automatically when this script
# returns with error: hence, collect logs manually on timeout.
if [[ $status -eq 124 || $status -eq 137 || $status -eq 1 ]]; then
  # man timeout(1) claims that it returns 124 if the command timed
  # out, and 137 if a KILL signal was used
  log 'Timeout detected: collecting logs manually'
  cleanup
  hts_log_collect_fail "${CTEST_TEST_NAME}"
  echo "${CTEST_TEST_NAME}" >> /opt/hts/log/error_summary
elif [[ $status -eq 0 ]]; then
  log 'test has passed collecting logs'
  cleanup
  hts_log_collect_success "${CTEST_TEST_NAME}"
fi

exit $status
