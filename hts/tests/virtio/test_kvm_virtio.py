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
import sys
import os
import time
import unittest
import logging
import libvirt
import argparse
import optparse
import logging
import traceback
import re
import random
import threading
import Queue

from optparse import OptionParser
sys.path.insert(0, "/opt/hts/")
from time import sleep
from infra import base
from infra import vm
from infra import helper
from infra import benchmark_helper
from infra import helper
from infra import const
from infra import thread_helper
from infra import traffic_helper
log = logging.getLogger('test' + '.' + __name__)


def read_options(options):
    global reboot_itr, num_vcpus, memory, mem_tolerence, max_vcpus, max_mem, block_size
    global on_off_itr, kernel_url, kernel_ver, krnl_cmp_itr, num_vm, iperf_threads
    global tap_ifname, bridge_name, eth_ifname, tap_type, iperf_length_size, iperf_bandwidth

    if options:
        reboot_itr = options.reboot_itr
        num_vcpus = options.num_vcpus
        memory = options.memory
        mem_tolerence = options.mem_tolerence
        max_vcpus = options.max_vcpus
        max_mem = options.max_mem
        block_size = options.block_size
        on_off_itr = options.on_off_itr
        kernel_url = options.kernel_url
        kernel_ver = options.kernel_ver
        krnl_cmp_itr = options.krnl_cmp_itr
        num_vm = options.num_vm
        tap_ifname = options.tap_ifname
        bridge_name = options.bridge_name
        eth_ifname = options.eth_ifname
        tap_type = options.tap_type
        iperf_threads = options.iperf_threads
        iperf_length_size = options.iperf_length_size
        iperf_bandwidth = options.iperf_bandwidth


if __name__ == '__main__':
    usage = 'python %prog --debug --physical --virtual(optional)'
    parser = OptionParser(description='Testing framework',
                          usage=usage)
    parser.add_option('--reboot_itr', dest='reboot_itr',
                      type="int", default='3',
                      help='reboot iteration')
    parser.add_option('--num_vcpus', dest='num_vcpus',
                      type="string", default='',
                      help='number of vcpus')
    parser.add_option('--memory', dest='memory',
                      type="string", default='',
                      help='memory size')

    parser.add_option('--mem_tolerence', dest='mem_tolerence',
                      type="int", default='10',
                      help='memory tolerence percentage')

    parser.add_option('--max_vcpus', dest='max_vcpus',
                      type="int", default='10',
                      help='maximum number of vcpus')

    parser.add_option('--max_mem', dest='max_mem',
                      type="int", default='32768',
                      help='maximum memory size')

    parser.add_option('--block_size', dest='block_size',
                      type='string', default='4,8,16',
                      help='block size for dd command')

    parser.add_option('--on_off_itr', dest='on_off_itr',
                      type='int', default='10',
                      help='on off iteration for cpu inside VM')

    parser.add_option('--kernel_url', dest='kernel_url',
                      type='string', default='https://www.kernel.org/pub/linux/kernel/v4.x/',
                      help='Upstream kernel url')

    parser.add_option('--kernel_ver', dest='kernel_ver',
                      type='string', default='linux-4.4.68',
                      help='kernel version')

    parser.add_option('--krnl_cmp_itr', dest='krnl_cmp_itr',
                      type='int', default='5',
                      help='kernel compilation iteration number')

    parser.add_option('--num_vm', dest='num_vm',
                      type='int', default='1',
                      help='maximum number of virtual machines to create')

    parser.add_option('--tap_ifname', dest='tap_ifname',
                      type='string', default='tap0',
                      help='name of tap interface')

    parser.add_option('--bridge_name', dest='bridge_name',
                      type='string', default='br0',
                      help='name of bridge interface')

    parser.add_option('--eth_ifname', dest='eth_ifname',
                      type='string', default='eth0',
                      help='name of wired interface, in-case of external host tap interface')

    parser.add_option('--tap_type', dest='tap_type',
                      type='string', default='default',
                      help='type of tap interface, can be {default}, {host_only} or {external}')

    parser.add_option('--iperf_length_size', dest='iperf_length_size',
                      type='string', default='128,256,512,1024,2048,4096,8192',
                      help='iperf length size')

    parser.add_option('--iperf_bandwidth', dest='iperf_bandwidth',
                      type="string", default='10M',
                      help='iperf bandiwdth for udp')

    parser.add_option('--iperf_threads', dest='iperf_threads',
                      type="int", default='2',
                      help='thread numbers for iperf')

    (options, args) = base.params_check(parser)
    base.read_options(options)
    read_options(options)


# This test will create a VM and will check if it is pingable
@base.CheckTestCaseEnabled
class VirtioTest01(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = num_vcpus
        self.memory = memory
        self.vm_args = ""

    def test_01_start_vm(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        helper.check_vm_health(self.credentials, ip)


# This test case will create a VM and will do reboot iterations
@base.CheckTestCaseEnabled
class VirtioTest02(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        log.info("Reboot iteration ptovided is %s", self.reboot_itr)
        self.num_vcpus = num_vcpus
        self.memory = memory
        self.vm_args = ""

    def test_01_reboot_vm(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        thread_helper.start_thread(target=vm_handle.wait_for_vm_boot,
                                   args=(domain, self.credentials, ),
                                   kwargs={'reboot': True}
                                   )
        vm_handle.vm_liveliness(domain)
        vm_handle.reboot_vm(domain, self.reboot_itr, self.credentials)
        ip = vm_handle.ip_address
        helper.check_vm_health(self.credentials, ip)
        helper.delete_all_vms(self.hyp_handle)
        thread_helper.join_all()


# This test case will create a VM and run iozone test cases on host and VM.
@base.CheckTestCaseEnabled
class VirtioTest03(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = num_vcpus
        self.memory = memory
        cmd = ("sudo fallocate -l 10GB /opt/tmpfs.img")
        helper.execute_cmd(cmd)
        cmd = ("sudo mkfs.ext4 -F /opt/tmpfs.img")
        helper.execute_cmd(cmd)
        self.vm_args = ""

    def test_03_run_iozone(self):
        log.info("Creating VM")
        self.vm_args = "--disk path=/opt/tmpfs.img,bus=virtio,perms=rw"
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        log.info("Running Iozone test on host machine")
        status = benchmark_helper.run_iozone_host(self.log_dir)
        if not status:
            raise Exception("Iozone tests failed on host")
        log.info("Running Iozone test on VM")
        status = benchmark_helper.run_iozone_vm(self.credentials, self.log_dir, ip)
        if not status:
            raise Exception("Iozone tests failed on vm")
        helper.check_vm_health(self.credentials, ip)

    def tearDown(self):
        log.info("Removing tmpfs.img")
        os.remove("/opt/tmpfs.img")


# This test will create a VM and will check if assigned memory and cpu
# is same inside VM.
@base.CheckTestCaseEnabled
class VirtioTest04(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.mem_tolerence = int(mem_tolerence)
        self.max_vcpus = int(max_vcpus)
        self.max_mem = int(max_mem)
        self.vm_args = ""

    def test_04_check_cpu_mem(self):
        for i in range(self.num_vcpus, self.max_vcpus):
            self.num_vcpus = i
            log.info("Creating VM")
            vm_handle = vm.Vminfo(self, self.hyp_handle)
            domain = vm_handle.create_vm()
            log.info("VM has been created with name %s", domain.name())
            vm_handle.wait_for_vm_boot(domain, self.credentials)
            vm_handle.vm_liveliness(domain)
            ip = vm_handle.ip_address
            mem = helper.check_vm_mem(self.credentials, ip)
            log.info("Total memory inside VM is %s" % mem)
            difference = int(self.memory) - int(mem)
            log.info("Memory difference between provided memory and allocated memory is %s" % difference)
            tolerence = ((float(self.mem_tolerence) / float(100)) * float(self.memory))
            log.info("Memory tolerence value is %s" % tolerence)
            if difference >= tolerence:
                raise Exception("Memory difference has exceed tolerence level")
            cpus = helper.check_vm_cpu_num(self.credentials, ip)
            log.info("CPUs allocated in VM is %s" % cpus)
            if self.num_vcpus != cpus:
                raise Exception("Number of CPUs provided do not match the number allocated")
            helper.check_vm_health(self.credentials, ip)
            helper.delete_all_vms(self.hyp_handle)
            if self.memory <= self.max_mem:
                self.memory += 1024


# This test case will create a VM and will online/offline cpu inside VM.
@base.CheckTestCaseEnabled
class VirtioTest05(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.on_off_itr = on_off_itr
        self.vm_args = ""

    def test_05_on_off_cpu(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        cpu_num = str(random.randint(1, self.num_vcpus - 1))
        log.info("CPU%s will be on/off" % cpu_num)
        for i in range(0, self.on_off_itr):
            helper.check_cpu_offline_vm(cpu_num, self.credentials, ip)
            helper.check_cpu_online_vm(cpu_num, self.credentials, ip)
        helper.check_vm_health(self.credentials, ip)


# This test case will create a VM and will online/offline cpu inside VM.
@base.CheckTestCaseEnabled
class VirtioTest06(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.vm_args = ""

    def test_05_on_off_cpu(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        for i in range(1, self.num_vcpus):
            helper.check_cpu_offline_vm(str(i), self.credentials, ip)
        for i in range(1, self.num_vcpus):
            helper.check_cpu_online_vm(str(i), self.credentials, ip)
        helper.check_vm_health(self.credentials, ip)


# This test case will create a VM and will run dd tests on vm
@base.CheckTestCaseEnabled
class VirtioTest07(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.block_size = block_size
        self.vm_args = ""

    def test_05_run_dd_cmd(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        block_list = []
        for i in self.block_size.split(","):
            block_list.append(int(i))
        cmd = ("sudo mkdir -p /mnt/dd-tests")
        output = helper.execute_cmd_vm_output(cmd, self.credentials, ip)
        log.info("Command output is %s" % output)
        for i in block_list:
            cmd = ("sudo time dd if=/dev/urandom of=/mnt/dd-tests/test bs=%dM count=10" % i)
            output = helper.execute_cmd_vm_output(cmd, self.credentials, ip)
            log.info("Command output is %s" % output)
            cmd = ("sudo rm -rf /mnt/dd-tests/test")
            output = helper.execute_cmd_vm_output(cmd, self.credentials, ip)
            log.info("Command output is %s" % output)
        helper.check_vm_health(self.credentials, ip)


# This test case will create a VM and will run ltp tests on vm and guest
@base.CheckTestCaseEnabled
class VirtioTest08(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.ltp_command = const.LTP_COMMAND
        self.vm_args = ""

    def test_08_test_ltp(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        benchmark_helper.run_ltp_on_vm(self.credentials, ip, self.log_dir, self.ltp_command)
        benchmark_helper.run_ltp_on_host(self.log_dir, self.ltp_command)
        helper.check_vm_health(self.credentials, ip)


# This test case will create a VM and will run ltp tests on vm and guest
@base.CheckTestCaseEnabled
class VirtioTest09(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.ltp_command = const.LTP_COMMAND
        self.vm_args = ""

    def test_09_test_gdb(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        benchmark_helper.run_gdb_on_vm(self.credentials, ip)
        helper.check_vm_health(self.credentials, ip)


# This test case will create a VM and will run ltp tests on vm and guest
@base.CheckTestCaseEnabled
class VirtioTest10(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.reboot_itr = reboot_itr
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.ltp_command = const.LTP_COMMAND
        self.vm_args = ""
        self.kernel_ver = kernel_ver
        self.kernel_url = kernel_url
        self.krnl_cmp_itr = krnl_cmp_itr

    def test_10_test_kbuild(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        benchmark_helper.cmpl_kernel_on_vm(self.credentials, ip, self.kernel_url, self.kernel_ver, self.krnl_cmp_itr)
        helper.check_vm_health(self.credentials, ip)


# This test will create multiple VM(s) and list their respective IP(s)
@base.CheckTestCaseEnabled
class VirtioTest11(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.num_vcpus = num_vcpus
        self.memory = memory
        self.vm_args = ""
        self.num_vm = num_vm
        self.vm_dir = {}
        self.domain_list = []
        helper.prepare_vm_snapshots(self.num_vm, self.arguments)

    def test_11_start_vm(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        # Create as many VM(s) specified by num_vm
        for i in xrange(self.num_vm):
            # Create a new VM in thread
            thread_helper.start_thread(target=vm_handle.create_vm,
                                       args=("test" + str(i),)
                                       )
        # Wait for threads to finish
        thread_helper.join_all()
        log.info("%d VM(s) created" % self.num_vm)
        # Deque each domain from thread return queue and wait for them to boot
        for i in xrange(self.num_vm):
            self.domain_list.append(thread_helper.return_queue.get())
            thread_helper.start_thread(target=vm_handle.wait_for_vm_boot,
                                       args=(self.domain_list[i], self.credentials,))
        thread_helper.join_all()
        # Store IP of each Vm created in test directory
        for i in xrange(self.num_vm):
            vm_handle.vm_liveliness(self.domain_list[i])
            self.vm_dir[self.domain_list[i].name()] = vm_handle.ip_address
        # Check VM health
        for keys, values in self.vm_dir.items():
            helper.check_vm_health(self.credentials, values)


# This test will create VMs and run iperf between them.
@base.CheckTestCaseEnabled
class VirtTest12(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.num_vcpus = num_vcpus
        self.memory = memory
        self.vm_args = ""
        self.num_vm = num_vm
        self.test_result = []
        self.tap_type = tap_type
        self.tap_ifname = tap_ifname
        self.bridge_name = bridge_name
        self.eth_ifname = eth_ifname
        self.dhcp = helper.create_tap_on_host(tap_type=self.tap_type,
                                              tap_ifname=self.tap_ifname,
                                              bridge_name=self.bridge_name,
                                              eth_ifname=self.eth_ifname
                                              )
        self.iperf_threads = iperf_threads
        self.iperf_length_size = iperf_length_size
        self.iperf_bandwidth = iperf_bandwidth

        helper.prepare_vm_snapshots(self.num_vm, self.arguments)

    def test_12_run_iperf(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        # Setup virt-install with tap interface
        self.vm_args = " --network bridge=%s,model=virtio" % self.bridge_name
        # Create 2 guests
        thread_helper.start_thread(target=vm_handle.create_vm, args=("test0",))
        thread_helper.start_thread(target=vm_handle.create_vm, args=("test1",))
        # Wait for threads to finish
        thread_helper.join_all()
        log.info("%d VM(s) created" % self.num_vm)
        # Configure TAP interface on guests
        thread_helper.start_thread(target=vm_handle.setup_tap_on_vm,
                                   args=(thread_helper.return_queue.get(), self.credentials,),
                                   kwargs={'dhcp': self.dhcp, 'tap_type': self.tap_type}
                                   )
        thread_helper.start_thread(target=vm_handle.setup_tap_on_vm,
                                   args=(thread_helper.return_queue.get(), self.credentials,),
                                   kwargs={'dhcp': self.dhcp, 'tap_type': self.tap_type}
                                   )
        # Wait for threads to finish
        thread_helper.join_all()
        # Get domain and IP of guests
        [domain0, ip0] = thread_helper.return_queue.get()
        [domain1, ip1] = thread_helper.return_queue.get()
        # Intll/configure iperf on VMs
        thread_helper.start_thread(target=benchmark_helper.configure_iperf_on_vm,
                                   kwargs={'credentials': None, 'ip': ip0, 'domain': domain0})
        thread_helper.start_thread(target=benchmark_helper.configure_iperf_on_vm,
                                   kwargs={'credentials': None, 'ip': ip1, 'domain': domain1})
        thread_helper.join_all()
        length_list = []
        for i in self.iperf_length_size.split(","):
            length_list.append(int(i))

        udp_bandwidth = self.iperf_bandwidth
        parallel_val = [False, self.iperf_threads]

        for par in parallel_val:
            if self.tap_type == "default":
                log.info("###########Running iperf between vms###########")
                iperf_server_ip = ip0
                iperf_client_ip = ip1
                iperf_server_credentials = domain0
                iperf_client_credentials = domain1

                traffic_helper.validate_iperf(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                              iperf_client_ip, length_list, parallel=par, telnet=True)
                traffic_helper.validate_iperf_udp(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                                  iperf_client_ip, length_list, udp_bandwidth, parallel=par, telnet=True)

                log.info("Reversing roles")
                iperf_server_ip = ip1
                iperf_client_ip = ip0
                iperf_server_credentials = domain1
                iperf_client_credentials = domain0

                traffic_helper.validate_iperf(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                              iperf_client_ip, length_list, parallel=par, telnet=True)
                traffic_helper.validate_iperf_udp(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                                  iperf_client_ip, length_list, udp_bandwidth, parallel=par, telnet=True)

            if self.tap_type == "host_only":
                log.info("###########Running iperf between host and VMs###########")
                iperf_server_ip = const.TAP_DEFAULT_IP
                iperf_client_ip = ip1
                iperf_server_credentials = False
                iperf_client_credentials = self.credentials

                traffic_helper.validate_iperf(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                              iperf_client_ip, length_list, parallel=par, telnet=False)
                traffic_helper.validate_iperf_udp(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                                  iperf_client_ip, length_list, udp_bandwidth, parallel=par, telnet=False)

                log.info("Reversing roles")
                iperf_server_ip = ip1
                iperf_client_ip = const.TAP_DEFAULT_IP
                iperf_server_credentials = self.credentials
                iperf_client_credentials = False

                traffic_helper.validate_iperf(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                              iperf_client_ip, length_list, parallel=par, telnet=False)
                traffic_helper.validate_iperf_udp(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                                  iperf_client_ip, length_list, udp_bandwidth, parallel=par, telnet=False)

            if self.tap_type == "external":
                ext_host_credentials = {'username': const.EXT_USERNAME, 'password': const.EXT_PASSWORD}
                log.info("###########Running iperf between vm and external host###########")
                iperf_server_ip = ip0
                iperf_client_ip = const.EXT_HOST_IP
                iperf_server_credentials = self.credentials
                iperf_client_credentials = ext_host_credentials

                traffic_helper.validate_iperf(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                              iperf_client_ip, length_list, parallel=par, telnet=False)
                traffic_helper.validate_iperf_udp(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                                  iperf_client_ip, length_list, udp_bandwidth, parallel=par, telnet=False)

                log.info("Reversing roles")
                iperf_server_ip = const.EXT_HOST_IP
                iperf_client_ip = ip0
                iperf_server_credentials = ext_host_credentials
                iperf_client_credentials = self.credentials

                traffic_helper.validate_iperf(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                              iperf_client_ip, length_list, parallel=par, telnet=False)
                traffic_helper.validate_iperf_udp(iperf_server_credentials, iperf_server_ip, iperf_client_credentials,
                                                  iperf_client_ip, length_list, udp_bandwidth, parallel=par, telnet=False)

    def tearDown(self):
        # Remove tap interface created on host
        helper.destroy_tap_on_host(tap_type=self.tap_type,
                                   bridge_name=self.bridge_name,
                                   eth_ifname=self.eth_ifname,
                                   tap_ifname=self.tap_ifname
                                   )


# This test will create VM and run LTP network tests between them.
@base.CheckTestCaseEnabled
class VirtioTest13(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.num_vcpus = num_vcpus
        self.memory = memory
        self.eth_ifname = eth_ifname
        self.vm_args = ""

    def test_13_run_ltp_network(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)

        ip = vm_handle.ip_address
        vm_ifname = helper.get_vm_net_ifname(domain)

        [rhost, lhost, ltp_network, ltp_network_rev] = benchmark_helper.setup_req_LTPNetwork(ip, self.credentials)

        self.ltp_network_args = (("RHOST=%s PASSWD=%s NS_DURATION=%s HTTP_DOWNLOAD_DIR=%s FTP_DOWNLOAD_DIR=%s "
                                  "FTP_UPLOAD_DIR=%s FTP_UPLOAD_URLDIR=%s IPV4_NETWORK=%s IPV4_NET_REV=%s "
                                  "RHOST_IPV4_HOST=%s LHOST_IPV4_HOST=%s LHOST_IFACES=%s RHOST_IFACES=%s ")
                                 % (self.credentials.get('username'), self.credentials.get('password'),
                                    const.NS_DURATION, const.HTTP_DOWNLOAD_DIR, const.FTP_DOWNLOAD_DIR, const.FTP_UPLOAD_DIR,
                                    const.FTP_UPLOAD_URLDIR, ltp_network, ltp_network_rev, rhost,
                                    const.LHOST_IPV4_HOST, self.eth_ifname, vm_ifname))

        self.ltp_command = "%s %s%s" % (self.ltp_network_args, const.LTP_DIR, const.LTP_NETWORK_COMMAND)
        benchmark_helper.run_ltp_on_host(self.log_dir, self.ltp_command, " ")


if __name__ == '__main__':
    unittest.main(verbosity=2, argv=([sys.argv[0]] + args))
