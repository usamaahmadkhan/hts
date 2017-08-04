#!/bin/bash

#This script will configure/install all tools/packages/dependencies required to
#execute Thunder-KVM test plan
#usage:
# bash build_kvm.sh

. /root/hts/build/scripts/bash_helpers.sh
. /root/hts/build/scripts/log_helpers.sh
. /root/hts/build/scripts/kvm-config

tryexec sudo chown -R $USER:$USER /opt/*
MAKE_JOBS=$(getconf _NPROCESSORS_ONLN)
arch=$(uname -m)
log "Host architecture is $arch"

#Installing QEMU dependencies
log "Insatalling QEMU dependencies"
tryexec sudo zypper install -y git
tryexec sudo zypper install -y zlib-devel
tryexec sudo zypper install -y libpixman-1-0-devel
tryexec sudo zypper install -y libfdt-devel
tryexec sudo zypper install -y libverto-glib-devel
tryexec sudo zypper install -y libgmpxx4
tryexec sudo zypper install -y libgnutlsxx-devel

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
tryexec sudo zypper install -y virt-manager

#Installing libvirt
log "Installing libvirt"
tryexec sudo zypper install -y libvirt

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
tryexec sudo zypper install -y iperf
tryexec sudo zypper install -y sshpass
tryexec sudo zypper install -y uml-utilities
tryexec sudo zypper install -y fio

#Installing python modules
log "Installing python modules"
tryexec sudo zypper install -y python
tryexec sudo zypper install -y python-pip
tryexec sudo zypper install -y python2-pexpect

#Installing pip packages
log "Installing pip packages"
for i in "${pip_dependencies[@]}"
do
   tryexec sudo pip install $i
done



#Configuring guest for qemu-guest-agent
log "Configuring qemu-guest-agent on host machine"
tryexec mkdir -p /var/lib/libvirt/qemu/channel/target
tryexec chown -R qemu /var/lib/libvirt/qemu/channel
tryexec echo "/var/lib/libvirt/qemu/channel/target/* rw," >> /etc/apparmor.d/abstractions/libvirt-qemu

#Installing some helper packages for arm arch
if [ "$arch" == "aarch64" ];then
    tryexec sudo zypper install -y qemu-system-arm
    tryexec sudo zypper install -y qemu-efi

else
    sudo sed -i '/#user = "root"/c\user = "root"' /etc/libvirt/qemu.conf
    sudo sed -i '/#group = "root"/c\group = "root"' /etc/libvirt/qemu.conf
fi
#Restarting libvirt service
log "Restarting libvirt service"
tryexec sudo service libvirtd restart
tryexec sudo service virtlogd restart
state=`sudo virsh net-list | grep default | awk '{print $2}'`
if [[ "$state" !=  "active" ]];then
    sudo virsh net-start default
fi

#Enable IPV4 forwarding
sysctl -w net.ipv4.ip_forward=1

#Installing LTP on host
log "Installing ltp on host"
bash /root/hts/build/scripts/install_ltp.sh
