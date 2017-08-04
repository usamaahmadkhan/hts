#!/usr/bin/python
#
# Copyright (c) 2017, Xgrid Inc, http://xgrid.co
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
SYSLOG_LOC_UBUNTU = "/var/log/syslog"
KERNEL_LOC_UBUNTU = "/var/log/kern.log"
SYSLOG_LOC_RHEL = "/var/log/messages"
DMESG_LOC = "/var/log/dmesg"
QEMULOG_LOC = "/var/log/libvirt/qemu/*"
SSH = "ssh -o StrictHostKeyChecking=no -o GSSAPIAuthentication=no -o UserKnownHostsFile=/dev/null"
SCP = "scp -o StrictHostKeyChecking=no -o GSSAPIAuthentication=no -o UserKnownHostsFile=/dev/null"
IOZONE_FILE = "iozone-host"
RETRY = 35
DEFAULT_XML = "<domain type='kvm'> <name>demo</name><uuid>7a5fdbd-cdaf-9455-926a-d65c16db1809</uuid>" \
              "<memory>4096000</memory><vcpu>2</vcpu><clock offset='utc'/><on_poweroff>destroy</on_poweroff>" \
              "<on_reboot>restart</on_reboot><on_crash>destroy</on_crash><devices>" \
              "<emulator>/usr/bin/qemu-system-x86_64</emulator><disk type='file' device='disk'>" \
              "<driver name='qemu' type='qcow2'/><source file='/usr/local/generic.qcow2'/><target dev='hda'/></disk>" \
              "<interface type='bridge'><mac address='52:54:00:56:78:65'/><source bridge='virbr0'/>" \
              "</interface><input type='mouse' bus='ps2'/><graphics type='vnc' port='-1' listen='127.0.0.1'/>" \
              "<channel type='unix'><source mode='bind'/><target type='virtio' name='org.qemu.guest_agent.0'/>" \
              "</channel></devices><os><type arch='x86_64' machine='pc'>hvm</type><boot dev='hd'/>" \
              "</os></domain>"
HTS_LOG_DIR = "/opt/hts/log"
LTP_COMMAND = "runltp -p -q -f io"
GDB_FILE_PATH = "/tmp/testcode.c"
VM_FILES_DIR = "/usr/local/"
VM_BOOT_LOG_FILE = "boot_log.txt"
VM_SNAPSHOT_ARGS = "bus=virtio,perms=rw,format=qcow2"
VM_LOGIN = "ubuntu login: "
VM_PASSWORD = "Password: "
VM_PROMPT = "ubuntu@ubuntu:~$ "
VM_SERIAL_ARGS = "mode=bind,protocol=telnet"
TELNET_HOST = "localhost"
TELNET_PORT = 2220
TAP_DEFAULT_IP = "20.0.0.1"
NET_PKT_SIZES = [64, 128, 256, 512, 1024, 1500]
NET_RTT_NAMES = ["NAME", "PKT_SIZE", "MIN", "AVG", "MAX", "MDEV", "IPG", "EWMA"]
NET_RTT_FILE = "network-rtt"
HOST_IP = "172.19.49.77"
HOST_USERNAME = "cavium"
HOST_PASSWORD = "cavium"
EXT_HOST_IP = "172.19.45.39"
EXT_USERNAME = "ahsan"
EXT_PASSWORD = "plumgrid"
IPERF_PORT = "5001"
IPERF_SVR_CMD = "iperf -s -D > tmp.txt"
IPERF_SVR_CMD_UDP = "iperf -s -u -D > tmp.txt"
LTP_NETWORK_COMMAND = "/testscripts/network.sh -mnrstcdaebiTURMFV "
LTP_DIR = "/opt/hts/ltp"
LTP_ENV_DIR = "/opt/hts/ltp/build/testcases/bin:/usr/bin:"
LHOST_IPV4_HOST = "1"
NS_DURATION = "60"
HTTP_DOWNLOAD_DIR = "/var/www/html"
FTP_DOWNLOAD_DIR = "/var/ftp"
FTP_UPLOAD_DIR = "/var/ftp/pub"
FTP_UPLOAD_URLDIR = "pub"
SPEC_FILES_IP = "10.22.28.100"
SPEC_FILES_HOST = "lcherian"
SPEC_FILES_PASSWD = "lcherian"
SPEC_FILES_PATH = "/opt/share/spec"
SPEC_2006_FILE = "spec2006-v1.2.tgz"
SPEC_2006_PATH = "/opt/SPEC"
SPEC_2006_DIR = SPEC_2006_PATH+"/spec2006"
SPEC_2006_URL = "http://www.spec.org/cpu2006/src.alt/linux-apm-arm64-118.tar"
SPEC_2006_ARM = "linux-apm-arm64-118.tar"
SPEC_2006_GIT = "git://12.108.191.254/toolchain/spec-configs.git"
SPEC_JBB_DRIVER_HOST = "ubuntu"
SPEC_JBB_DRIVER_PASSWD = "ubuntu"
SPEC_JBB_DRIVER_IP = "10.22.28.79"
SPEC_JBB_PATH = "/opt/SpecjbbTest"
SPEC_JBB_FILE = "specjbb2013_sources.tgz"
SPEC_JBB_JDK_VER = "1704"
SPEC_JBB_JDK_FILE = "jdk7-server-release-"+SPEC_JBB_JDK_VER+".tar.xz"
SPEC_JBB_JDK_URL = "http://openjdk.linaro.org/releases/"+SPEC_JBB_JDK_FILE
SPEC_JBB_DIR = SPEC_JBB_PATH+"/SPECjbb2013-source"
