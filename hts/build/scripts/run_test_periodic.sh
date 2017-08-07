#!/bin bash
#This script will run test cases for kvm-functional-periodic-x86 pipeline.
. /root/hts/hts/build/scripts/log_helpers.sh
path=/root/hts/hts/build
pushd $path &> /dev/null
log "Listing all tests"
ctest -N
log "Running all tests"
log "ctest --output-on-failure -R $1"
ctest --output-on-failure -R $1
status=$?
popd &> /dev/null
sudo chown -R $USER:$USER /tmp/*
sudo chown -R $USER:$USER /opt/hts/*
cp /opt/hts/log/error_summary $WORKSPACE/logs
cp /root/hts/hts/summary_log $WORKSPACE/logs
cp -r /tmp/*_log $WORKSPACE/logs
exit $status
