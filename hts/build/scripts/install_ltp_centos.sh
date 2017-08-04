#!/bin/bash

source /root/hts/build/scripts/bash_helpers.sh
source /root/hts/build/scripts/log_helpers.sh
source /root/hts/scripts/ltp_config

# Export language settings
tryexec export LANG=C
tryexec export LC_ALL=C

# PREREQS on CentOS (package-list is incomplete and may vary for other distros)
log "Installing pre-requisite packages"
tryexec sudo yum install gcc gcc-c++ kernel-devel make -y
tryexec sudo yum install autoconf automake m4 -y
tryexec sudo yum install git -y
tryexec sudo yum install libaio-devel libcap-devel -y

# Working directory
log "Creating LTP working directory"
VERSION=20170116
tryexec sudo rm -rf /opt/ltp
tryexec sudo mkdir -p /opt/ltp
tryexec pushd /opt/ltp &> /dev/null

# Get the LTP source
log "Cloning LTP source"
tryexec sudo wget https://github.com/linux-test-project/ltp/releases/download/$VERSION/ltp-full-$VERSION.tar.xz

# Configure LTP
log "Configuring LTP source"
tryexec sudo tar --strip-components=1 -Jxf ltp-full-$VERSION.tar.xz

# Start building LTP
log "Building LTP"
tryexec sudo mkdir build
tryexec sudo ./configure --prefix=$PREFIX

# Install LTP (requires superuser privileges)
log "Installing LTP"
tryexec sudo make all
tryexec sudo make SKIP_IDCHECK=1 install
tryexec popd &> /dev/null

#Run LTP Network setup
log "Configuring LTP Network Environment"
tryexec sudo bash /root/hts/scripts/setup_env_centos.sh
