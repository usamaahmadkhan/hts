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
import random
import os
import logging
import sys
import time
import traceback
import subprocess
import sys
import datetime
import pexpect
import textwrap
import mmap
sys.path.insert(0, "/opt/hts/")
from subprocess import call
from infra import helper
from infra import const
log = logging.getLogger('test' + '.' + __name__)


def run_iozone_host(log_dir):
    """
    This function will run iozone tests on the host machine from whewre the test has been executed.
    args:
    log_dir: Name of directory where tests result will be saved.
    """
    file_name_xls = "%s/%s.xls" % (log_dir, const.IOZONE_FILE)
    file_name_csv = "%s/%s.csv" % (log_dir, const.IOZONE_FILE)
    helper.create_file(file_name_xls)
    helper.create_file(file_name_csv)
    log.info("Running Iozone tests on host now...")
    cmd = ("iozone -a -b %s" % (file_name_xls))
    helper.execute_cmd(cmd)
    helper.xls_to_csv_converter(file_name_xls, file_name_csv)
    return True


def run_iozone_vm(credentials, log_dir, ip):
    """
    This function will run iozone tests on the VM.
    args:
    credentials: Dictionary having VM credentials.
    log_dir: Directory where logs will be stored.
    ip: IP of the VM.
    """
    dirname = "%s/%s" % (log_dir, const.IOZONE_FILE)
    username = credentials.get('username')
    password = credentials.get('password')
    log.info("VM username is  %s and password is %s " % (username, password))
    filename_xls = "iozone-guest-%s.xls" % ip
    filename_csv = "%s/iozone-guest-%s.csv" % (log_dir, ip)
    helper.create_file(filename_csv)
    cmd = ("sshpass -p %s  %s %s@%s 'touch ~/%s'" % (password, const.SSH, username, ip, filename_xls))
    helper.execute_cmd(cmd)
    helper.check_dpkg_lock(credentials, ip)
    cmd = ("sshpass -p %s  %s %s@%s 'sudo apt-get install iozone3 -y'" % (password, const.SSH, username, ip))
    helper.execute_cmd(cmd)
    cmd = ("sudo mkdir /mnt2")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("lsblk --noheadings | grep disk")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    devices = output.strip()
    log.info("Devices present inside VM are %s " % devices)
    cmd = ("cat /proc/mounts")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    for device in devices.splitlines():
        device_name = device.split(" ")[0]
        if device_name not in output:
            mnt_device = device_name
    log.info("/dev/%s will be used as mounting device inside VM" % mnt_device)
    cmd = ("sudo mount /dev/%s /mnt2" % mnt_device)
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    log.info("Running Iozone tests on VM now...")
    cmd = ("sshpass -p %s  %s %s@%s 'cd /mnt2;sudo iozone -a -b ~/%s'" % (
        password, const.SSH, username, ip, filename_xls
    ))
    helper.execute_cmd(cmd)

    log.info("Copying iozone logs from VM")
    cmd = ("sshpass -p %s  %s %s@%s:~/%s  %s" % (password, const.SCP, username, ip, filename_xls, log_dir))
    helper.execute_cmd(cmd)
    xls_file = "%s/%s" % (log_dir, filename_xls)
    helper.xls_to_csv_converter(xls_file, filename_csv)
    return True


def run_ltp_on_vm(credentials, ip, log_dir, ltp_command):
    """
    This function will install/build ltp on guest and run ltp tests
    args:
    credentials: Credentials of guest
    ip: IP of guest
    log_dir: Directory where logs will be stored
    ltp_command: ltp network script with switches
    """
    ltp_build_log = "build-log.txt"
    ltp_install_log = "install-log.txt"
    working_dir = "$HOME/src/ltp"
    ltp_prefix = "/opt/ltp"
    git_url = "https://github.com/linux-test-project/ltp.git"
    filename = "ltp-guest-%s.txt" % ip
    ltp_prefix = "/opt/ltp"

    cmd = ("export LANG=C")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("export LC_ALL=C")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    helper.check_dpkg_lock(credentials, ip)
    log.info("Installing some dependencies for ltp")
    cmd = ("sudo apt-get update -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install build-essential -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install autoconf automake autotools-dev m4 -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install git -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install libaio-dev libattr1-dev libcap-dev -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)

    log.info("Making some directories for installing ltp in VM")
    cmd = ("mkdir -p %s" % working_dir)
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo mkdir -p %s" % ltp_prefix)
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("getconf _NPROCESSORS_ONLN")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    jobs = output.strip()

    log.info("Installing ltp now")
    cmd = ("cd %s;git clone %s ltp-git" % (working_dir, git_url))
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("cd %s/ltp-git/;make autotools" % working_dir)
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("cd %s/ltp-git/;./configure --prefix=%s" % (working_dir, ltp_prefix))
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("cd %s/ltp-git/;make -j%s 2>&1 | tee ../%s" % (working_dir, jobs, ltp_build_log))
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("cd %s/ltp-git/;sudo make install 2>&1 | tee ../%s" % (working_dir, ltp_install_log))
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    log.info("Running ltp tests now")
    if ltp_command != " ":
        cmd = ("sudo bash %s/%s -o ~/%s" % (ltp_prefix, ltp_command, filename))
        output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
        file_path = ("~/%s" % filename)
        output = helper.scp_vm_to_host(credentials, ip, file_path, log_dir)


def run_ltp_on_host(log_dir, ltp_command, ltp_prefix="/opt/hts/ltp"):
    """
    This function will run ltp tests on host
    args:
    log_dir: directory eherre logs will be stored
    ltp_command: Command to run ltp tests
    ltp_prefix: default path of the ltp test suite
    """
    file_name = "%s/ltp_host.txt" % log_dir
    helper.create_file(file_name)
    log.info("Running ltp tests on host now...")
    if ltp_prefix == "/opt/hts/ltp":
        cmd = ("sudo bash %s/%s -o %s" % (ltp_prefix, ltp_command, file_name))
        helper.execute_cmd(cmd)
    else:
        cmd = ("%s | tee %s" % (ltp_command, file_name))
        helper.execute_cmd(cmd)
        f = open(file_name)
        s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        if s.find('TFAIL') != -1:
            raise Exception("LTP network test has failed")


def run_gdb_on_vm(credentials, ip):
    """
    This function will run gdb test on vm.
    args:
    credentials: Credentials of guest
    ip: IP of guest
    """

    code = """
           #include<stdio.h>
           int main()
           {
           int i=5;
           printf("i value is %d", i);
           return 0;
           }
           """
    code = textwrap.dedent(code)
    with open("%s" % const.GDB_FILE_PATH, "w") as text_file:
        text_file.write(code)
    dst_path = "~/"
    output = helper.scp_host_to_vm(credentials, ip, const.GDB_FILE_PATH, dst_path)
    helper.check_dpkg_lock(credentials, ip)
    cmd = ("sudo apt-get update -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install build-essential -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install gcc gdb -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("gcc -g ~/testcode.c -o test")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    username = credentials.get('username')
    password = credentials.get('password')
    child = pexpect.spawn("%s %s@%s" % (const.SSH, username, ip))
    child.expect('.*password:')
    child.sendline(password)
    child.expect('.*~')
    child.sendline("gdb ~/test")
    child.expect('.*gdb')
    child.sendline("b main")
    child.expect('.*gdb')
    child.sendline("run")


def cmpl_kernel_on_vm(credentials, ip, kernel_url, kernel_ver, itr):
    """
    This function will compile a kernel on vm.
    args:
    credentials: Credentials of guest
    ip: IP of guest
    kernel_url: url of kernel to be compiled
    kernel_ver: version of the kernel to be compiled
    itr: number of compilation iteration
    """
    cmd = ("wget %s/%s.tar.xz" % (kernel_url, kernel_ver))
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    helper.check_dpkg_lock(credentials, ip)
    cmd = ("sudo apt-get update -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install gcc make bc -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("tar -xf ~/%s.tar.xz" % kernel_ver)
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("getconf _NPROCESSORS_ONLN")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    jobs = output.strip()
    cmd = ("cd ~/%s;make defconfig" % kernel_ver)
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("cd %s;for i in seq {1..%s};do make -j%s;make clean;done" % (kernel_ver, itr, jobs))
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)


def run_fio_on_vm(credentials, ip, log_dir, block_list, io_pattern, runtime):
    """
    This function will run fio benchmark tool on VM.
    args:
    credentials: Credentials of guest
    ip: IP of guest
    block_list: list of block sizes to be used
    io_pattern: io_pattern to be used
    runtime: run time of fio command
    """
    helper.check_dpkg_lock(credentials, ip)
    cmd = ("sudo apt-get update -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install fio -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    for j in range(2):
        for i in block_list:
            filename = "fio-vm-%s-%s-direct%s" % (i, io_pattern, j)
            cmd = ("fio --name=test  --numjobs=2  --filesize=1G --bs=%s  --rw=%s --ioengine=libaio --direct=%s"
                   " --sync=0 --norandommap --group_reporting --runtime=%s --time_based"
                   " --output=/home/ubuntu/%s" % (i, io_pattern, j, runtime, filename))
            output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
            file_path = "/home/ubuntu/%s" % filename
            output = helper.scp_vm_to_host(credentials, ip, file_path, log_dir)


def run_fio_on_host(log_dir, block_list, io_pattern, runtime):
    """
    This function will run fio benchmark tool on host.
    args:
    block_list: list of block sizes to be used
    io_pattern: io_pattern to be used
    runtime: run time of fio command
    """
    for j in range(2):
        for i in block_list:
            filename = "fio-host-%s-%s-direct%s" % (i, io_pattern, j)
            cmd = ("fio --name=test  --numjobs=2  --filesize=1G --bs=%s  --rw=%s --ioengine=libaio --direct=%s"
                   " --sync=0 --norandommap --group_reporting --runtime=%s --time_based"
                   " --output=%s/%s" % (i, io_pattern, j, runtime, log_dir, filename))
            output = helper.execute_cmd_output(cmd)


def configure_stressng_on_vm(credentials, ip):
    """
    This function will configure/install stressng benchmark tool on VM.
    args:
    credentials: Credentials of guest
    ip: IP of guest
    """
    helper.check_dpkg_lock(credentials, ip)
    cmd = ("sudo apt-get update -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo apt-get install build-essential -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("cd /tmp/;git clone https://github.com/ColinIanKing/stress-ng")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("cd /tmp/stress-ng;make")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)
    cmd = ("sudo cp /tmp/stress-ng/stress-ng /usr/bin")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=False)


def run_network_latency_test(credentials, ip, domain=None):
    """
    This function runs network latency tests on VM
    args:
    credentials: login parameters of VM
    ip: VM IP
    domain: VM handle
    """
    # Create an empty dictionary to store results
    result = list()
    # Network type (loopback/Virtio) is decided on whether domain is provided
    if domain is None:
        log.info("Running loop-back latency Test")
    else:
        log.info("Running Virtio latency Test")
    # Run test for different packet sizes
    for pkt in const.NET_PKT_SIZES:
        log.info("Running for pakcet size: %d" % pkt)
        if domain is None:
            # Perform loopback latency test
            cmd = "sudo ping -q -f 127.0.0.1 -s %d -w 60 | grep rtt" % pkt
            # Execute command on VM via SSH and get output
            output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)
            # Parse output
            tmp = output.split(' ')
        else:
            # Perform Virtio latency test
            cmd = "sudo ping -q -f %s -s %d -w 60 | grep rtt" % (ip, pkt)
            # Execute command on VM via telnet and get output
            output = helper.execute_cmd_vm_telnet(domain, cmd)
            # Parse output
            tmp = output.split('rtt')[2].split(' ')
        # Extract result data from output
        result.append([str(pkt)] + tmp[3].split('/') + tmp[6].split('/'))
    return result


def configure_iperf_on_vm(credentials=None, ip=None, domain=None):
    """
    This function will configure/install iperf tool on VM.
    args:
    credentials: Credentials of guest
    ip: IP of guest
    domain: Handle of VM
    """
    log.info("configure_iperf_on_vm")
    cmd = ("sudo apt-get update -y")
    output = helper.exe_command_vm(cmd, credentials, ip, domain=domain, root=False)
    cmd = ("sudo apt-get install build-essential -y")
    output = helper.exe_command_vm(cmd, credentials, ip, domain=domain, root=False)
    cmd = ("sudo apt-get install iperf -y")
    output = helper.exe_command_vm(cmd, credentials, ip, domain=domain, root=False)


def run_spec_2006_on_host(log_dir):
    result_path = "%s/spec2006-host-result/" % log_dir
    cmd = "sudo mkdir -p %s"
    helper.execute_cmd(cmd)
    output = helper.execute_cmd_output(cmd)
    cmd = "runspec --config t99.upstream.lp64.config --noreportable --iterations 1 --rebuild int"
    output = helper.execute_cmd_output(cmd)
    cmd = "runspec --config t99.upstream.lp64.config --noreportable --iterations 1 --rebuild fp"
    output = helper.execute_cmd_output(cmd)
    cmd = "runspec --config t99.upstream.lp64.config --noreportable --iterations 1 --rebuild --rate 32 int"
    output = helper.execute_cmd_output(cmd)
    cmd = "runspec --config t99.upstream.lp64.config --noreportable --iterations 1 --rebuild --rate 32 fp"
    output = helper.execute_cmd_output(cmd)
    cmd = "sudo cp /opt/hts/spec2006/result/* %s" % result_path
    output = helper.execute_cmd_output(cmd)
    cmd = "sudo rm -r /opt/hts/spec2006/result/"
    output = helper.execute_cmd_output(cmd)


def run_spec2006_on_vm(log_dir, credentials, ip):
    """
    This function will download, install and run spec2006 benchmarks on VM
    args:
    log_dir: Log directory of host to save results
    credentials: Login credentials of VM
    ip: VM IP
    """
    result_path = "%s/spec2006-guest-result/" % log_dir
    cmd = "sudo mkdir -p %s" % result_path
    helper.execute_cmd(cmd)
    helper.check_dpkg_lock(credentials, ip)
    cmd = ("sudo apt-get update -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = ("sudo apt-get install git -y")
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "mkdir -p %s" % const.SPEC_2006_PATH
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "sudo sshpass -p %s %s %s@%s:%s/%s %s" % (const.SPEC_FILES_PASSWD,
                                                    const.SCP,
                                                    const.SPEC_FILES_HOST,
                                                    const.SPEC_FILES_IP,
                                                    const.SPEC_FILES_PATH,
                                                    const.SPEC_2006_FILE,
                                                    const.SPEC_2006_PATH)
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "pushd %s &> /dev/null" % const.SPEC_2006_PATH
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "tar -xvf %s" % const.SPEC_2006_FILE
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "popd &> /dev/null"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "pushd %s &> /dev/null" % const.SPEC_2006_DIR
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "chmod -R a+w ."
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)
    cmd = "wget %s" % const.SPEC_2006_URL
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "tar xf %s" % const.SPEC_2006_ARM
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "yes yes | sh install.sh"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "git clone %s" % const.SPEC_2006_GIT
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "cp spec-configs/speccpu2006/t99.upstream.lp64.config config"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "source shrc"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)
    cmd = "popd &> /dev/null"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "runspec --config t99.upstream.lp64.config --noreportable --iterations 1 --rebuild int"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "runspec --config t99.upstream.lp64.config --noreportable --iterations 1 --rebuild fp"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "runspec --config t99.upstream.lp64.config --noreportable --iterations 1 --rebuild --rate 32 int"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "runspec --config t99.upstream.lp64.config --noreportable --iterations 1 --rebuild --rate 32 fp"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    vm_spec_result_path = "%s/result" % const.SPEC_2006_DIR
    helper.scp_vm_to_host(credentials, ip, vm_spec_result_path+"/*", result_path)


def run_specjbb_on_vm(credentials=None, ip=None):
    cmd = "mkdir -p %s" % const.SPEC_JBB_PATH
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)
    scp_host_dir = "%s/%s" % (const.SPEC_JBB_PATH, const.SPEC_JBB_FILE)
    scp_vm_dest = const.SPEC_JBB_PATH
    helper.scp_host_to_vm(credentials, ip, scp_host_dir, scp_vm_dest)
    cmd = "pushd %s &> /dev/null" % const.SPEC_JBB_PATH
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "tar -xvf %s" % const.SPEC_JBB_FILE
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)
    cmd = "wget %s" % const.SPEC_JBB_JDK_URL
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)
    cmd = "tar -xvf %s" % const.SPEC_JBB_JDK_FILE
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)
    cmd = "export JAVA_HOME=%s/jdk7-server-release-%s/bin/java >> /root/.bashrc" % (
        const.SPEC_JBB_PATH,
        const.SPEC_JBB_JDK_VER
    )
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "export PATH=%s/jdk7-server-release-%s/bin/:$PATH >> /root/.bashrc" % (
        const.SPEC_JBB_PATH,
        const.SPEC_JBB_JDK_VER
    )
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)
    cmd = "update-alternatives --install '/usr/bin/java' \
     'java' '%s/jdk7-server-release-%s/bin/java' 1" % (const.SPEC_JBB_PATH,
                                                       const.SPEC_JBB_JDK_VER
                                                       )
    output = helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)
    cmd = "popd &> /dev/null"
    output = helper.execute_cmd_vm_output(cmd, credentials, ip)


def install_spec_2013(driver=None, credentials=None, ip=None):
    if credentials:
        credentials['username'] = 'root'
        child = pexpect.spawn("%s -t %s@%s 'cd %s;bash'" % (const.SSH,
                                                            credentials.get('username'),
                                                            ip,
                                                            const.SPEC_JBB_DIR
                                                            )
                              )
        child.expect('.*password:')
        child.sendline(credentials.get('password'))
    else:
        if driver:
            credentials = dict()
            credentials['username'] = 'root'
            credentials['password'] = 'ubuntu'
            child = pexpect.spawn("%s -t %s@%s 'cd %s;bash'" % (const.SSH,
                                                                credentials.get('username'),
                                                                ip,
                                                                const.SPEC_JBB_DIR
                                                                )
                                  )
            child.expect('.*password:')
            child.sendline(credentials.get('password'))
        else:
            child = pexpect.spawn("cd %s" % const.SPEC_JBB_DIR)
    child.expect('.*%s' % const.SPEC_JBB_DIR)
    child.sendline('java -jar SPECjbb2013-1.00-Setup.jar')
    child.expect('CHOOSE LOCALE BY NUMBER: ')
    child.sendline('\r')
    for i in xrange(0, 7):
        child.expect('PRESS <ENTER> TO CONTINUE: ')
        child.sendline('\r')
    child.expect('DO YOU ACCEPT THE TERMS OF THIS LICENSE AGREEMENT? (Y/N): ')
    child.sendline('y\r')
    child.expect('      : ')
    child.sendline('/opt/hts/SpecjbbTest/SPECjbb2013\r')
    child.expect('   IS THIS CORRECT? (Y/N): ')
    child.sendline('y\r')
    child.expect('PRESS <ENTER> TO CONTINUE: ')
    child.sendline('\r')
    child.expect('PRESS <ENTER> TO INSTALL: ')
    child.sendline('\r')
    for i in xrange(0, 2):
        child.expect('PRESS <ENTER> TO CONTINUE: ')
        child.sendline('\r')
    child.expect('IMPORTANT INFORMATION COMPLETE. PRESS <ENTER> TO CONTINUE: ')
    child.sendline('\r')
    child.expect('PRESS <ENTER> TO EXIT THE INSTALLER: ')
    child.sendline('\r')


def setup_req_LTPNetwork(ip, credentials):
    """
    This function will run necessary commands on host
    and return necessary variables for running LTP network
    args details:
    ip: VM ip
    credentials: credential details of VM
    """
    ltp_network = ip.split('.')[0] + "." + ip.split('.')[1] + "." + ip.split('.')[2]
    ltp_network_rev = ip.split('.')[2] + "." + ip.split('.')[1] + "." + ip.split('.')[0]

    lhost = ltp_network + "." + const.LHOST_IPV4_HOST
    rhost = ip.split('.')[3]

    cmd = "echo "+ip+" "+credentials.get('username')+" >> /etc/hosts"
    helper.execute_cmd(cmd)
    cmd = "yes y | ssh-keygen -f id_rsa -t rsa -N \'"+ip+"\'"
    helper.execute_cmd(cmd)
    cmd = "cat $HOME/.ssh/id_rsa.pub"
    output = helper.execute_cmd_output(cmd)
    output = output.split('\n')[0]
    cmd = "echo export PATH="+const.LTP_ENV_DIR+"\$PATH >> $HOME/.bashrc"
    helper.execute_cmd(cmd)
    cmd = "echo \'/ "+lhost+"/255.255.255.0(rw,no_root_squash,sync)\' >> /etc/exports"
    helper.execute_cmd_output(cmd)
    cmd = "echo "+output+" >> /root/.ssh/authorized_keys"
    helper.execute_cmd_vm_output(cmd, credentials, ip, root=True)

    return (rhost, lhost, ltp_network, ltp_network_rev)
