#!/bin/bash

#This script will configure/install all tools/packages/dependencies required to
#execute Thunder-KVM test plan
#usage:
# bash build_kvm.sh

. /root/hts/hts/build/scripts/bash_helpers.sh
. /root/hts/hts/build/scripts/log_helpers.sh
. /root/hts/hts/build/scripts/kvm-config

tryexec sudo chown -R $USER:$USER /opt/*
MAKE_JOBS=$(getconf _NPROCESSORS_ONLN)
arch=$(uname -m)
log "Host architecture is $arch"

#Installing QEMU dependencies
log "Insatalling QEMU dependencies"
for i in "${qemu_dependencies[@]}"
do
   log "Installing $i"
   tryexec sudo apt-get install $i -y
done

#Installing/configuring QEMU
log "Installing/configuring QEMU"
tryexec mkdir -p $qemu_dir
tryexec pushd $qemu_dir &> /dev/null
if [[ -z "${QEMU_VERSION}" ]];then
    qemu_ver=$qemu_version
else
    qemu_ver=${QEMU_VERSION}'.tar.xz'
fi

log "QEMU source is $qemu_url/$qemu_ver"
tryexec wget  $qemu_url/$qemu_ver
tryexec tar -xvf $qemu_ver &> /dev/null
tryexec pushd qemu-* &> /dev/null
if [ "$arch" == "aarch64" ];then
    tryexec ./configure --target-list=aarch64-softmmu --enable-kvm  --enable-fdt --prefix=/usr
else
    tryexec ./configure --target-list=x86_64-softmmu --enable-kvm  --enable-fdt --prefix=/usr
fi
tryexec make -j$MAKE_JOBS
tryexec sudo make install
tryexec popd &> /dev/null
tryexec popd &> /dev/null

log "Installing virt-manager"
tryexec sudo apt-get install virt-manager -y

#Installing libvirt
log "Installing libvirt"
tryexec sudo apt-get install libvirt-bin -y

#Installing benchmarking tools in host machine
log "installing benchmarking tools"
tryexec mkdir "/opt/hts/iozone-src"
tryexec pushd "/opt/hts/iozone-src" &> /dev/null
tryexec wget http://www.iozone.org/src/current/iozone3_465.tar
tryexec tar -xvf iozone*.tar
tryexec pushd iozone*/src/current &> /dev/null
if [ "$arch" == "aarch64" ];then
    tryexec make linux-arm
else
    tryexec make linux-AMD64
fi
tryexec sudo cp iozone /usr/bin/
tryexec popd &> /dev/null
tryexec popd &> /dev/null
tryexec sudo apt-get install iperf -y
tryexec sudo apt-get install sshpass -y
tryexec sudo apt-get install uml-utilities -y
tryexec sudo apt-get install fio -y

#Installing python modules
log "Installing python modules"
tryexec sudo apt-get install python -y
tryexec sudo apt-get install python-pip -y

#Installing pip packages
log "Installing pip packages"
for i in "${pip_dependencies[@]}"
do
   tryexec sudo pip install $i
done

#Configuring guest for qemu-guest-agent
log "Configuring qemu-guest-agent on host machine"
tryexec sudo bash /root/hts/hts/build/scripts/conf_qemu_agent.sh

#Installing some helper packages for arm arch
if [ "$arch" == "aarch64" ];then
    tryexec sudo apt-get install qemu-system-arm -y
    tryexec sudo apt-get install qemu-efi -y

else
    sudo sed -i '/#user = "root"/c\user = "root"' /etc/libvirt/qemu.conf
    sudo sed -i '/#group = "root"/c\group = "root"' /etc/libvirt/qemu.conf
fi
#Restarting libvirt service
log "Restarting libvirt service"
tryexec sudo service libvirt-bin restart
tryexec sudo service virtlogd restart
state=`sudo virsh net-list | grep default | awk '{print $2}'`
if [[ "$state" !=  "active" ]];then
    sudo virsh net-start default
fi

#Enable IPV4 forwarding
sysctl -w net.ipv4.ip_forward=1

#Installing LTP on host
log "Installing ltp on host"
bash /root/hts/hts/build/scripts/install_ltp.sh
