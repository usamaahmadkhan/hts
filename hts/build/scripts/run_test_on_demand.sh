#!/bin bash
#This script will run test cases for kvm-functional-periodic-x86 pipeline.
. /root/hts/hts/build/scripts/log_helpers.sh
path=/root/hts/hts/build
pushd $path &> /dev/null
log "Listing all tests"
ctest -N
if [ "${TEST_NAME}" == "all" ];then
    log "Running all tests"
    ctest --output-on-failure -R
    status=$?
else
    log "Running test ${TEST_NAME}"
    ctest --output-on-failure -R ${TEST_NAME}
    status=$?
fi
popd &> /dev/null
sudo chown -R $USER:$USER /tmp/*
cp -r /tmp/*_log $WORKSPACE/logs
exit $status
