#!/bin/bash
#This script will build hts project

sudo zypper install --no-confirm gcc gcc-c++ kernel-devel make
sudo zypper install --no-confirm cmake
sudo mkdir -p /opt/hts
sudo chown -R $USER:$USER /opt/*
mkdir -p logs
mkdir build
pushd build &> /dev/null
cmake -DCMAKE_CXX_COMPILER=/usr/bin/c++ ..
popd &> /dev/null
sudo rm -rf /tmp/*_log
