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
import time
import unittest
import logging
import logging
import optparse

sys.path.insert(0, "/opt/hts/")
from optparse import OptionParser
from time import sleep
from infra import base
from infra import vm
from infra import helper
from infra import benchmark_helper
from infra import const
from infra import thread_helper
log = logging.getLogger('test' + '.' + __name__)


def read_options(options):
    global reboot_itr, num_vcpus, memory, mem_tolerence, max_vcpus, max_mem, stressng_timeout, stressng_inst_num

    if options:
        reboot_itr = options.reboot_itr
        num_vcpus = options.num_vcpus
        memory = options.memory
        max_vcpus = options.max_vcpus
        max_mem = options.max_mem
        stressng_timeout = options.stressng_timeout
        stressng_inst_num = options.stressng_inst_num

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

    parser.add_option('--max_vcpus', dest='max_vcpus',
                      type="int", default='10',
                      help='maximum number of vcpus')

    parser.add_option('--max_mem', dest='max_mem',
                      type="int", default='32768',
                      help='maximum memory size')

    parser.add_option('--stressng_timeout', dest='stressng_timeout',
                      type='string', default='2m',
                      help='Time to run stress-ng command')

    parser.add_option('--stressng_inst_num', dest='stressng_inst_num',
                      type='string', default='4',
                      help='Number of instances of each stress test')

    (options, args) = base.params_check(parser)
    base.read_options(options)
    read_options(options)


# This test case will create a VM and will run stress-ng tests with option --all on vm
@base.CheckTestCaseEnabled
class StressngTest01(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.vm_args = ""
        self.stressng_timeout = stressng_timeout
        self.stressng_inst_num = stressng_inst_num

    def test_01_stressng_all(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        stressng_cmd = ("stress-ng -a %s --timeout %s" % (self.stressng_inst_num, self.stressng_timeout))
        log.info("stress-ng command is %s" % (stressng_cmd))
        benchmark_helper.configure_stressng_on_vm(self.credentials, ip)
        output = helper.execute_cmd_vm_output(stressng_cmd, self.credentials, ip, root=False)
        helper.check_vm_health(self.credentials, ip)


# This test case will create a VM and will run stress-ng tests with io and os classes on vm
@base.CheckTestCaseEnabled
class StressngTest02(base.BaseTest):
    sleep_time = 2

    def setUp(self):
        self.num_vcpus = int(num_vcpus)
        self.memory = int(memory)
        self.vm_args = ""
        self.stressng_timeout = stressng_timeout
        self.stressng_inst_num = stressng_inst_num

    def test_02_stressng_class(self):
        log.info("Creating VM")
        vm_handle = vm.Vminfo(self, self.hyp_handle)
        domain = vm_handle.create_vm()
        log.info("VM has been created with name %s", domain.name())
        vm_handle.wait_for_vm_boot(domain, self.credentials)
        vm_handle.vm_liveliness(domain)
        ip = vm_handle.ip_address
        stressng_cmd1 = ("stress-ng --class os --all %s --timeout %s" % (self.stressng_inst_num, self.stressng_timeout))
        log.info("stress-ng command is %s" % (stressng_cmd1))
        stressng_cmd2 = ("stress-ng --class io --all %s --timeout %s" % (self.stressng_inst_num, self.stressng_timeout))
        log.info("stress-ng command is %s" % (stressng_cmd2))
        benchmark_helper.configure_stressng_on_vm(self.credentials, ip)
        thread_helper.start_thread(target=helper.execute_cmd_vm_output, args=(stressng_cmd1, self.credentials, ip,))
        thread_helper.start_thread(target=helper.execute_cmd_vm_output, args=(stressng_cmd2, self.credentials, ip,))
        thread_helper.join_all()
        helper.check_vm_health(self.credentials, ip)


if __name__ == '__main__':
    unittest.main(verbosity=2, argv=([sys.argv[0]] + args))
