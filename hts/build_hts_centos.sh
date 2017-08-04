#!/bin/bash
# This script will build hts project

sudo yum install gcc gcc-c++ kernel-devel make -y
sudo yum install cmake -y
sudo mkdir -p /opt/hts
sudo mkdir -p /opt/hts/log
sudo touch /opt/hts/log/error_summary
sudo chown -R $USER:$USER /opt/*
mkdir -p logs
mkdir build
pushd build &> /dev/null
cmake ..
popd &> /dev/null
sudo rm -rf /tmp/*_log
