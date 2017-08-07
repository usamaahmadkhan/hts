#!/bin/bash
#This script will build hts project

sudo zypper install --no-confirm gcc gcc-c++ kernel-devel make
wget https://cmake.org/files/v3.8/cmake-3.8.2.tar.gz
sudo mkdir -p /opt/hts
sudo mkdir -p /opt/hts/cmake-src
pushd /opt/hts/cmake-src &> /dev/null
sudo wget https://cmake.org/files/v3.8/cmake-3.8.2.tar.gz
sudo gzip -d cmake-3.8.2.tar.gz
sudo tar -xvf cmake-3.8.2.tar cmake-3.8.2/
popd &> /dev/null
sudo chown -R $USER:$USER /opt/*
mkdir -p logs
mkdir build
pushd build &> /dev/null
cmake -DCMAKE_CXX_COMPILER=/usr/bin/c++ ..
popd &> /dev/null
sudo rm -rf /tmp/*_log
