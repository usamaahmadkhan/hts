#!/bin/bash

if [[ -n "$LOG_HELPERS_INCLUDED" ]]; then
  return 0
fi
LOG_HELPERS_INCLUDED=1

# Include bash_helpers from the same directory we were included from:
# we cannot guarantee that the client script has setup a proper PATH.
bash_h_name="$(dirname ${BASH_SOURCE})/bash_helpers.sh"
. "${bash_h_name}"
status=$?
if [[ "$status" -ne 0 ]]; then
  echo 'Cannot find bash_helpers.sh! Exiting.'
  exit 3
fi

# INTERNAL routine to collect logs. Requires:
# $1: test name (possibly unsanitized)
# $2: FAIL or PASS filename component
function hts_log_collect_internal() {
  if [[ $# -lt 2 ]]; then
    log "BUG: ${FUNCNAME} received $# arguments"
    return
  fi

  if [[ ! -d /opt/hts/log/ ]]; then
    log '/opt/hts/log is not a directory, cannot collect hts logs'
    return
  fi

  # cleanup the test name, just in case the caller did not do it
  local testname=$(echo "$1" | tr -d -C '[:alnum:]_')

  local faildir=${EXPORT_FAILURES_DIR:-/tmp}
  local filename=$(mktemp -d "${faildir}/$(date '+%Y%m%d_%H%M%S')_${2}_${testname}_XXXXXX_log")
  log "Collecting hts logs into ${filename} ..."
  pushd /opt/hts/log &> /dev/null
  sudo mv */* "${filename}"
  popd &> /dev/null
}

##################################################

# Collect hts logs upon test failure. The name of the test should
# be provided as the first parameter.
function hts_log_collect_fail() {
  if [[ $# -lt 1 ]]; then
    log 'Test name not provided, cannot collect hts logs'
    return
  fi

  hts_log_collect_internal "${1}" 'FAIL'
}

# Collect hts logs after a successful test. The name of the test
# should be provided as the first parameter.
function hts_log_collect_success() {
  if [[ $# -lt 1 ]]; then
    log 'Test name not provided, cannot collect hts logs'
    return
  fi

  hts_log_collect_internal "${1}" 'PASS'
}
