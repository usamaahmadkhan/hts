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
import json

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
log = logging.getLogger('test' + '.' + __name__)


def read_options(options):
    global reboot_itr, num_vcpus, memory, mem_tolerence, block_size, krnl_cmp_itr, io_pattern, runtime
    global tap_ifname, bridge_name, eth_ifname, tap_type, num_vm

    if options:
        reboot_itr = options.reboot_itr
        num_vcpus = options.num_vcpus
        memory = options.memory
        block_size = options.block_size
        io_pattern = options.io_pattern
        runtime = options.runtime
        num_vm = options.num_vm
        tap_ifname = options.tap_ifname
        bridge_name = options.bridge_name
        eth_ifname = options.eth_ifname
        tap_type = options.tap_type

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
    parser.add_option('--block_size', dest='block_size',
                      type='string', default='4k,8k,16k,32k,64k,128k,256k,512k',
                      help='block size for fio command')
    parser.add_option('--io_pattern', dest='io_pattern',
                      type='str', default='read',
                      help='default io pattern for fio')
    parser.add_option('--runtime', dest='runtime',
                      type='str', default='100',
                      help='defaulr runtime')
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

    (options, args) = base.params_check(parser)
    base.read_options(options)
    read_options(options)


# This test will create a VM and will check if it is pingable
@base.CheckTestCaseEnabled
class PerfTest01(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.reboot_itr = reboot_itr
        self.num_vcpus = num_vcpus
        self.memory = memory
        self.vm_args = ""
        self.io_pattern = io_pattern
        self.runtime = runtime
        self.block_size = block_size

    def test_01_run_fio(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        block_list = []
        for i in self.block_size.split(","):
            block_list.append(i)
        log.info("block list provided is %s" % self.block_size)
        log.info("Running FIO on host now...")
        benchmark_helper.run_fio_on_host(self.log_dir, block_list, self.io_pattern, self.runtime)
        log.info("Running FIO on VM now...")
        benchmark_helper.run_fio_on_vm(self.credentials, ip, self.log_dir, block_list, self.io_pattern, self.runtime)
        helper.check_vm_health(self.credentials, ip)


# This test will create a VM and check network latency
@base.CheckTestCaseEnabled
class PerfTest02(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.num_vcpus = num_vcpus
        self.memory = memory
        self.vm_args = ""
        self.num_vm = num_vm
        self.test_result = dict()
        self.tap_type = tap_type
        self.tap_ifname = tap_ifname
        self.bridge_name = bridge_name
        self.eth_ifname = eth_ifname
        self.dhcp = helper.create_tap_on_host(tap_type=self.tap_type,
                                              tap_ifname=self.tap_ifname,
                                              bridge_name=self.bridge_name,
                                              eth_ifname=self.eth_ifname
                                              )
        helper.prepare_vm_snapshots(self.num_vm, self.arguments)

    def test_02_network_latency(self):
        # Create 1 guest
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        # Wait for guest to boot and get its IP
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        # Run network loopback latency test on guest and store result in dictionary
        self.test_result['Loop-Back'] = benchmark_helper.run_network_latency_test(self.credentials, ip)
        # Remove guest
        domain.destroy()
        domain.undefine()
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
        # Run network Virtio latency test on guest and store result in dictionary
        self.test_result['VirtIO'] = benchmark_helper.run_network_latency_test(
            self.credentials, ip0, domain=domain1
        )
        # Dump result data in file
        filename = "%s/%s" % (self.log_dir, const.NET_RTT_FILE)
        with open(filename, 'w') as outfile:
            outfile.write("\t\t".join(const.NET_RTT_NAMES) + "\n")
            for test_name, results in self.test_result.items():
                for result in results:
                    outfile.write(test_name + "\t\t" + "\t\t".join(result) + "\n")
        outfile.close()

    def tearDown(self):
        # Remove tap interface created on host
        helper.destroy_tap_on_host(tap_type=self.tap_type,
                                   bridge_name=self.bridge_name,
                                   eth_ifname=self.eth_ifname,
                                   tap_ifname=self.tap_ifname
                                   )

if __name__ == '__main__':
    unittest.main(verbosity=2, argv=([sys.argv[0]] + args))
