#!/bin/bash

source /root/hts/hts/build/scripts/bash_helpers.sh
source /root/hts/hts/build/scripts/log_helpers.sh
source /root/hts/hts/scripts/ltp_config

# Export language settings
tryexec export LANG=C
tryexec export LC_ALL=C

# PREREQS on Ubuntu (package-list is incomplete and may vary for other distros)
log "Installing pre-requisite packages"
tryexec sudo zypper install -y gcc gcc-c++ kernel-devel make cmake
tryexec sudo zypper install -y autoconf automake m4
tryexec sudo zypper install -y git
tryexec sudo zypper install -y libaio-devel libattr1 libcap-devel

# Working directory
log "Creating LTP working directory"
tryexec mkdir -p $WORKING_DIR
tryexec sudo mkdir -p $PREFIX
tryexec sudo chown -R $USER:$USER $PREFIX
pushd $WORKING_DIR &> /dev/null

# Get the LTP source
log "Cloning LTP source"
tryexec git clone $GIT_URL ltp-git

# Configure LTP
log "Configuring LTP source"
pushd ltp-git/ &> /dev/null
tryexec make autotools
tryexec ./configure --prefix=$PREFIX

# Start building LTP
log "Building LTP"
tryexec make -j$MAKE_JOBS 2>&1 | tee ../$BUILD_LOG_FILE

# Install LTP (requires superuser privileges)
log "Installing LTP"
tryexec sudo make install 2>&1 | tee ../$INSTALL_LOG_FILE

#Run LTP Network setup
log "Configuring LTP Network Environment"
tryexec sudo bash /root/hts/hts/scripts/setup_env_suse.sh
