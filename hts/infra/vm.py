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

import os
import re
import sys
import ConfigParser
import logging
import helper
import uuid
import libvirt
import subprocess
import time
import telnetlib
sys.path.insert(0, "/opt/hts/")

from time import sleep
from infra import const
from infra import thread_helper
log = logging.getLogger('test' + '.' + __name__)


class Vminfo():
    """
    Class that defines information about each VM
    """
    def __init__(self, testhand, hosthand):

        self.hosthand = hosthand
        self.testhand = testhand
        self.vm_name = testhand.__class__.__name__
        self.memory = "2048"
        self.num_vcpus = "2"
        self.image_file = ""
        dict_conf = {}
        self.ip_address = ""
        self.credentials = testhand.credentials
        self.arguments = testhand.arguments
        self.extra_arguments = testhand.extra_arguments
        self.telnet_port = const.TELNET_PORT

    def create_vm(self, vm_name=None):
        """
        This function will create VM and return handle of VM
        args:
        vm_name: thread name which corresponds to VM name
        """
        # If vm_name is passed in arguments change test arguments w.r.t vm_name
        if vm_name is not None:
            # Change conf.yaml arguments w.r.t thread parameters
            self.arguments["name"] = vm_name
            self.arguments["disk"] = "path=%s%s.qcow2,%s" % (const.VM_FILES_DIR, vm_name, const.VM_SNAPSHOT_ARGS)
        self.arguments["serial"] = "tcp,host=:%d,%s" % (self.telnet_port, const.VM_SERIAL_ARGS)
        self.telnet_port += 1
        vm_name = self.arguments.get('name')
        vm_string = helper.get_vm_string(self.testhand, self.arguments, self.extra_arguments)
        vm_command = ("virt-install --connect qemu:///system  %s" % vm_string)
        helper.execute_cmd(vm_command)
        dom = self.hosthand.lookupByName(vm_name)
        log.info("VM has been created")
        return dom

    def get_ip_address(self, handle):
        """
        This function will get IP asddress of VM.
        args:
        handle: Handle of VM.
        """
        ip_address = None
        for i in range(const.RETRY):
            log.info("Retry %s for getting IP address" % i)
            try:
                ifaces = handle.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
            except:
                pass
            else:
                for (name, val) in ifaces.iteritems():
                    if name != "lo":
                        if val['addrs']:
                            for ipaddr in val['addrs']:
                                if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                                    ip_address = ipaddr['addr']
                                    log.info("IP address of vm is %s", ip_address)
            if ip_address is not None:
                break
            time.sleep(7)
        if ip_address is None:
            raise Exception("QEMU Driver error : Guest agent is not responding")
        self.ip_address = ip_address
        return ip_address

    @staticmethod
    def check_vm_connectivity(ip_address, state="ON"):
        """
        This function will check VM connectivity by pinging the IP provided.
        args:
        ip_address: IP of VM.
        itr: Number for ping iteration.
        state: state of vm to be checked
        """
        log.info("Checking vm connectivity for %s", ip_address)
        for ping in range(const.RETRY):
            res = subprocess.call(['ping', '-c', '3', ip_address])
            if res == 0 and state == "ON":
                log.info("ping to ip %s has passed", ip_address)
                return True
            if res != 0 and state == "OFF":
                log.info("ping to ip %s has failed", ip_address)
                return True

        raise Exception("Checking state %s of VM with IP %s has failed", (state, ip_address))

    def vm_liveliness(self, handle, ip_address=None):
        """
        This function will check if VM is alive.
        args:
        handle: Handle of VM.
        ip_address: IP of VM.
        """
        vm_name = handle.name()
        result = handle.isActive()
        if not result:
            raise Exception("VM  %s is not active", vm_name)
        log.info("VM %s is active", vm_name)
        log.info("Getting VM IP address")
        if ip_address is None:
            ip_address = self.get_ip_address(handle)
        status = self.check_vm_connectivity(ip_address, state="ON")
        if not status:
            raise Exception("VM  %s is active but not pingable", vm_name)
        return True

    def reboot_vm(self, handle, itr, credentials):
        """
        This function will reboot VM.
        args:
        handle: Handle of VM.
        itr: Number of VM reboot.
        credentials: Credentials of vm
        """
        log.info("Rebooting VM")
        ip_address = self.get_ip_address(handle)
        for i in range(itr):
            log.info("Rebooting VM %s iteration %s" % ((handle.name()), i))
            cmd = ("sudo virsh reboot %s" % ((handle.name())))
            helper.execute_cmd(cmd)
            self.check_vm_connectivity(ip_address, state="OFF")
            log.info("VM has restarted.Now test will wait for vm to come up and get ip address again")
            ip_address = self.get_ip_address(handle)
            self.vm_liveliness(handle, ip_address=ip_address)
            log.info("Running command lscpu on vm to check if shell is accessible")
            cmd = ("lscpu")
            output = helper.execute_cmd_vm_output(cmd, credentials, ip_address)

    def wait_for_vm_boot(self, handle, credentials, reboot=False):
        """
        This function will wait for VM to boot and dump boot log in a txt file
        args:
        handle: libvirt object that holds information about VM
        credentials: login credentials of VM
        """
        host = const.TELNET_HOST
        port = int(helper.get_vm_telnet_port(handle))
        if port is None:
            raise Exception("Cannot open telnet session with %s VM" % handle.name())
        # Open telnet session with VM
        tn = telnetlib.Telnet(host, port)
        login_prompt = const.VM_LOGIN
        # Create file for saving boot log of VM
        filename = "%s/%s_%s" % (self.testhand.log_dir, handle.name(), const.VM_BOOT_LOG_FILE)
        vm_file = open(filename, "w")
        if reboot:
            boot_log = tn.read_all()
            vm_file.write(boot_log)
            vm_file.close()
            tn.close()
        else:
            # Save boot log in file and wait until login prompt
            while True:
                boot_log = tn.read_until(login_prompt, 5)
                vm_file.write(boot_log)
                if login_prompt in boot_log:
                    vm_file.close()
                    break
                log.info("Waiting for VM to boot...")
                time.sleep(10)
            log.info(
                "Logging into VM %s with username: %s and password: %s" %
                (handle.name(), credentials.get('username'), credentials.get('password'))
            )
            # Login to VM using test login credentials
            tn.write(credentials.get('username') + "\r\n")
            tn.read_until(const.VM_PASSWORD)
            tn.write(credentials.get('password') + "\r\n")
            tn.read_until(const.VM_PROMPT)
            # Close telnet session
            tn.close()

    @staticmethod
    def set_vm_ip(handle, ip=None, dhcp=False):
        """
        This function opens a telnet session with VM and set IP of VM
        args:
        handle: libvirt object that holds information about VM
        ip: IP to be configured; in-case of dhcp this is ignored, else use series defined in const.py
        dhcp: configure IP using DHCP protocol in-case of external tap interface
        """
        host = const.TELNET_HOST
        port = int(helper.get_vm_telnet_port(handle))
        if port is None:
            raise Exception("Cannot open telnet session with %s VM" % handle.name())
        vm_ifname = helper.get_vm_net_ifname(handle)
        # Open telnet session with VM
        tn = telnetlib.Telnet(host, port)
        # If ip is not given configure VM with const.TAP_DEFAULT_IP series
        if ip is None:
            ip = const.TAP_DEFAULT_IP[:-1] + str(port - (const.TELNET_PORT - 2))
        # If dhcp run DHCP on VM else configure VM with ip
        if dhcp:
            log.info("Running DHCP on VM %s" % handle.name())
            tn.write("sudo dhclient %s\r\n" % vm_ifname)
            tn.read_until(const.VM_PROMPT)
        else:
            log.info("Setting up VM IP: %s" % ip)
            tn.write("sudo ifconfig %s %s up\r\n" % (vm_ifname, ip))
            tn.read_until(const.VM_PROMPT)
        # Close telnet session
        tn.close()

    def setup_tap_on_vm(self, handle, credentials, ip=None, dhcp=False, tap_type='default'):
        """
        This function will
        -wait for the VM to boot and perform boot log
        -configure IP w.r.t type of tap interface
        args:
        handle: libvirt object that holds information about VM
        credentials: login credentials of VM
        ip: IP to be configured; in-case of dhcp this is ignored, else use series defined in const.py
        dhcp: configure IP using DHCP protocol in-case of external tap interface
        """
        self.wait_for_vm_boot(handle, credentials)
        self.set_vm_ip(handle, ip, dhcp)
        if tap_type != 'default':
            self.vm_liveliness(handle)
        else:
            self.get_ip_address(handle)
        return [handle, self.ip_address]
