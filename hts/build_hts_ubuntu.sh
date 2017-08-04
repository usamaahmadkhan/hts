#!/bin/bash
# This script will build hts project

sudo apt-get install build-essential -y
sudo apt-get install cmake -y
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
