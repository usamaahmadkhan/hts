#!/bin/bash

if [[ -n "$BASH_HELPERS_INCLUDED" ]]; then
  return 0
fi
BASH_HELPERS_INCLUDED=1

##################################################

# Logs a message to stdout, prefixing the message with the script
# name and the current date.
function log() {
  echo "[$(basename $0)-$(date '+%H:%M:%S.%N')] $@"
}

# Logs a message  to stdout, prefixing the message with the script
# name, current date and the hostname.
function log_hostname() {
  echo "[$(basename $0)-$(date '+%H:%M:%S.%N')->$(uname -n)] $@"
}

# Logs a message to stderr, prefixing the message with the script
# name and the current date.
function logerr() {
  echo "[$(basename $0)-$(date '+%H:%M:%S.%N')] $@" >&2
}

# Logs a a message to stdout, prefixing the message with the script
# name and the current date, then call exit with a nonzero value. The
# current stack trace is also printed to help debugging.
function logexit() {
  log "$@"
  print_stack
  exit 1
}

# Logs a message to stderr, prefixing the message with the script
# name and the current date, then call exit with a nonzero value.
function logerrexit() {
  logerr "$@"
  exit 1
}

# Try to execute a command. If the command returns success, this
# function returns 0. Otherwise, the script is aborted with the status
# code of the failed command, and the current stack trace is printed
# to help debugging.
function tryexec() {
  "$@"
  retval=$?
  [[ $retval -eq 0 ]] && return 0

  log 'A command has failed:'
  log "  $@"
  log "Value returned: ${retval}"
  print_stack
  exit $retval
}
