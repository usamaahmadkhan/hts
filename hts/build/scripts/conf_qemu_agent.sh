#!/bin/bash
#This script will configure dependencies required to use qemu-guest-agent.

. /root/hts/build/scripts/bash_helpers.sh

tryexec mkdir -p /var/lib/libvirt/qemu/channel/target
tryexec chown -R libvirt-qemu:kvm /var/lib/libvirt/qemu/channel
tryexec echo "/var/lib/libvirt/qemu/channel/target/* rw," >> /etc/apparmor.d/abstractions/libvirt-qemu
