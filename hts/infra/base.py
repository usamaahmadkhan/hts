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

import logging
import optparse
import re
import os
import sys
import time
import datetime
import subprocess
import traceback
import ConfigParser
import unittest
import random
import libvirt
from optparse import OptionParser
sys.path.insert(0, "/opt/hts/")
from infra import helper
log = logging.getLogger('test' + '.' + __name__)

test_pattern = '.*'
debug_flag = ""
userlog = "info"
conf_file = ""


def params_check(parser=None):
    usage = 'sudo python %prog --debug(optional)'

    if not parser:
        parser = OptionParser(description='Testing framework', usage=usage)
    parser.add_option("--debug", dest='debug_flag', action="store_true",
                      default=False, help='debugging mode')
    parser.add_option('--test_pattern', dest='test_pattern', metavar='PAT',
                      default='.*', help='Run tests which match pattern PAT')
    parser.add_option("--loglevel", dest='userlog', type="string",
                      default="info", help='logging level')
    parser.add_option('--conf', dest='conf_file', type="str", default='conf.yaml',
                      help='configuration file  of VM')

    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        sys.exit(2)
    return (options, args)


def read_options(options):
    global test_pattern, debug_flag, userlog, conf_file
    if options:
        debug_flag = options.debug_flag
        test_pattern = options.test_pattern
        userlog = options.userlog.capitalize()
        conf_file = options.conf_file


class BaseTest(unittest.TestCase):
    """
    Abstract class that defines the structure of a test case.
    In your own test module, derive from this class and define the
    setUp and test_* methods. The classmethod setUpClass may be
    overritten, but make sure to call the parent setUpClass as the first
    step.
    """

    @classmethod
    def setUpClass(cls):
        """
        This is a setup class, it will be called before the test case called.
        Tasks which are same for every test case will be executed here.
        args:
        cls: test case class to match
        """
        conf_credentials = {}
        cls.log_dir = helper.create_log(cls.__name__, userlog)

        file_path = os.path.abspath(conf_file)
        cls.credentials, cls.arguments, cls.extra_arguments = helper.read_conf_file(file_path)
        log.info("Opening connection with qemu")
        cls.hyp_handle = libvirt.open('qemu:///system')
        if cls.hyp_handle is None:
            raise Exception("Failed to open connection to qemu:///system")
        cls.start_time = time.strftime("%H:%M:%S")
        helper.copy_vm_image()

    @classmethod
    def tearDownClass(cls):
        """
        This is a teardown class, it will be called after the test case called.
        Tasks which are same for every test case will be executed here.
        args:
        cls: test case class to match
        """
        helper.collect_system_logs(cls.log_dir)
        log.info("Deleting all VMs")
        helper.delete_all_vms(cls.hyp_handle)
        log.info("Closing connection with hypervisor")
        cls.hyp_handle.close()
        log.info("Connection with hypervisor has been closed")
        cls.stop_time = time.strftime("%H:%M:%S")
        helper.check_host_health(cls.start_time, cls.stop_time)


def CheckTestCaseEnabled(cls):
    """
    Decorator function to enable/disable whole test cases
    args:
    cls:  test case class to match
    """
    (tp1, sep, tp2) = test_pattern.partition('\\.')
    if tp1 == '':
        tp1 = '.*'
    if not re.match('^' + tp1 + '$', cls.__name__):
        class Empty(unittest.TestCase):
            @unittest.skip('skipping test case %s' % cls.__name__)
            def test_empty(self):
                pass
        return Empty
    return cls
