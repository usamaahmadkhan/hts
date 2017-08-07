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
import uuid
import ConfigParser
import xlrd
import unicodecsv
import yaml
import re
import pexpect
import telnetlib
import platform
import libvirt

sys.path.insert(0, "/opt/hts/")
import datetime
from subprocess import call
from optparse import OptionParser
from infra import const
from xml.etree import ElementTree as et
from xml.dom import minidom

log = logging.getLogger('test' + '.' + __name__)


def rand_mac():
    """
    Generate random mac address
    return: mac address
    """
    log.info("creating random mac")
    mac = "52:54:00:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255))
    return mac


def delete_all_vms(hypervisor_handle):
    """
    This function will remove all the VMs present in a hypervisor.
    args:
    hypervisor_handle: Handle of hypervisor.
    """
    domains = hypervisor_handle.listAllDomains(0)
    if len(domains) != 0:
        for domain in domains:
            log.info("Deleting VM %s", domain.name())
            if domain.isActive() == 1:
                domain.destroy()
            if get_host_arch() == "aarch64":
                execute_cmd("sudo virsh undefine --nvram %s" % domain.name())
            else:
                domain.undefine()
    else:
        log.info("No VM found")


def execute_cmd(cmd):
    """
    Execute any bash command and raise exception if it fails.
    args:
    cmd: command to be run
    """
    log.info("Executing command %s on host" % cmd)
    try:
        subprocess.check_call(cmd, shell=True)
    except:
        raise Exception("Command %s has failed with output" % cmd)


def execute_cmd_output(cmd):
    """
    Execute any bash command and raise exception if it fails.
    args:
    cmd: command to be run
    """
    log.info("Executing command %s on host" % cmd)
    try:
        output = subprocess.check_output(cmd, shell=True)
    except:
        raise Exception("Command %s has failed with output" % cmd)
    return output


def execute_cmd_vm_output(cmd, credentials, ip, root=False, check=True):
    """
    Execute any bash command and raise exception if it fails.
    args:
    cmd: command to be run
    """
    if root:
        username = "root"
    else:
        username = credentials.get('username')
    password = credentials.get('password')
    vm_cmd = ("sshpass -p %s  %s %s@%s '%s'" % (password, const.SSH, username, ip, cmd))
    log.info("Executing command %s on vm" % vm_cmd)
    try:
        output = subprocess.check_output(vm_cmd, shell=True)
    except:
        if check:
            raise Exception("Command %s has failed" % vm_cmd)
        else:
            pass
            output = None
    return output


def scp_vm_to_host(credentials, ip, vm_file, host_dst):
    """
    This function will scp files from vm
    args:
    credentials: Credentials of VM
    ip: ip of vm
    vm_file:  File to be copied
    host_dst: Directory where file need to be copied
    """
    username = credentials.get('username')
    password = credentials.get('password')
    vm_cmd = ("sshpass -p %s  %s %s@%s:%s  %s" % (password, const.SCP, username, ip, vm_file, host_dst))
    log.info("Executing command %s on vm" % vm_cmd)
    try:
        output = subprocess.check_output(vm_cmd, shell=True)
    except:
        raise Exception("Command %s has failed" % vm_cmd)

    return output


def scp_host_to_vm(credentials, ip, host_file, vm_dst):
    """
    This function will scp files from vm
    args:
    credentials: Credentials of VM
    ip: ip of vm
    host_file:  File to be copied
    vm_dst: Directory where file need to be copied
    """
    username = credentials.get('username')
    password = credentials.get('password')
    vm_cmd = ("sshpass -p %s  %s %s %s@%s:%s" % (password, const.SCP, host_file, username, ip, vm_dst))
    log.info("Executing command %s on vm" % vm_cmd)
    try:
        output = subprocess.check_output(vm_cmd, shell=True)
    except:
        raise Exception("Command %s has failed" % vm_cmd)

    return output


def create_log(test_name, userlog):
    """
    This function will create log_dir and log_file and will open it for logging.
    args:
    test_name: test_name
    return: log_dir path
    """
    os.environ['TZ'] = 'US/Pacific'
    time.tzset()

    time_now = datetime.datetime.now()
    iso_time = datetime.datetime.isoformat(time_now)
    log_dir = "%s/%s_debuglog_.%s" % (const.HTS_LOG_DIR, test_name, iso_time)
    log_file = "%s/test_case.log" % log_dir

    # create the log directory and opens the file debug_log to log events
    if not log_dir_initialize(log_dir, log_file):
        print __name__ + ' Could not open debug log dir: %s' % log_dir
        print __name__ + ' Debug output will be on stdout'
    else:
        log.info('Logging to dir: ' + log_dir)
    if userlog == "Debug":
        loglevel = logging.DEBUG
    elif userlog == "Info":
        loglevel = logging.INFO
    elif userlog == "Warning":
        loglevel = logging.WARNING
    elif userlog == "Critical":
        loglevel = logging.CRITICAL
    else:
        loglevel = logging.ERROR

    format = ("[%(levelname)s %(asctime)s.%(module)s.%(lineno)d] %(message)s")
    formatter = logging.Formatter("[%(levelname)s-%(asctime)s-%(module)s.%(lineno)d]%(message)s")

    logger_ = logging.getLogger('test')
    logger_.setLevel(loglevel)
    hdlr_ = logging.FileHandler(log_file, mode='w')
    hdlr_.setFormatter(formatter)
    logger_.addHandler(hdlr_)
    stderr_log_handler = logging.StreamHandler()
    stderr_log_handler.setFormatter(formatter)
    logger_.addHandler(stderr_log_handler)

    return log_dir


def log_dir_initialize(dirname, log_file):
    """
    This function will open log_file for storing logs.
    args:
    log_dir: Directory of log_file.
    log_file: Name of file.
    """
    global dir_name
    dir_name = dirname

    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except Exception:
            log.info(" log_dir_initialize:Error creating log directory or \
              opening file..logged only on console")
            return False
    try:
        logfile = open(log_file, 'w')
    except Exception as e:
        log.info(" log_dir_initialize:Error creating log file")
        return False
    return True


def read_conf_file(file_path):
    """
    This function create a dictionary of conf file passed
    args:
    file_path: path of configuration file.
    """
    with open('conf.yaml', 'r') as f:
        try:
            content = yaml.load(f)
        except:
            raise Exception("Error reading configuration file")
    credentials = content["credentials"]
    arguments = content["arguments"]
    extra_arguments = content["extra_arguments"]
    log.info("VM arguments provided are %s" % arguments)
    log.info("VM credentials provided are %s" % credentials)
    log.info("VM extra arguments provided are %s" % extra_arguments)
    return credentials, arguments, extra_arguments


def get_vm_string(testhand, arguments, extra_arguments):
    """
    This function will create VM string for virt install command.
    args:
    testhand: test handle
    arguments: arguments provided by user in conf file
    extra_arguments: flags provided by user in conf file
    """
    vm_string = ""
    if testhand.num_vcpus:
        arguments["vcpus"] = testhand.num_vcpus
    if testhand.memory:
        arguments["memory"] = testhand.memory
    for key, value in arguments.items():
        if key == "disk":
            key = "import --%s" % key
        vm_string += "--%s %s " % (key, value)

    for i in extra_arguments:
        vm_string += "--%s " % i
    arch = get_host_arch()
    vm_string += "--arch %s " % arch

    if testhand.vm_args:
        vm_string += testhand.vm_args

    log.info("VM string is %s" % vm_string)
    return vm_string


def collect_system_logs(log_dir):
    """
    collect system logs
    args:
    log_dir
    """
    log.info("Collecting system logs")
    log.info("Collecting system syslog")
    if "Ubuntu" in platform.platform():
        cmd = ("cp -R %s %s" % (const.SYSLOG_LOC_UBUNTU, log_dir))
    elif "centos" in platform.platform():
        cmd = ("cp -R %s %s" % (const.SYSLOG_LOC_RHEL, log_dir))
    elif "SuSE" in platform.platform():
        cmd = ("cp -R %s %s" % (const.SYSLOG_LOC_RHEL, log_dir))
    execute_cmd(cmd)
    log.info("Collecting system kernel log")
    if "Ubuntu" in platform.platform():
        cmd = ("cp -R %s %s/kernel_log" % (const.KERNEL_LOC_UBUNTU, log_dir))
        execute_cmd(cmd)
    log.info("Collecting qemu log")
    cmd = ("cp -R %s %s" % (const.QEMULOG_LOC, log_dir))
    execute_cmd(cmd)


def collect_vm_logs(log_dir, credentials, ip):
    """
    collect system logs
    args:
    log_dir
    """
    log.info("Collecting vm syslog")
    vm_file = "%s" % const.SYSLOG_LOC_UBUNTU
    dst_file = "%s/vm-syslog" % log_dir
    scp_vm_to_host(credentials, ip, vm_file, dst_file)

    log.info("Collecting vm kernel log")
    vm_file = "%s " % (const.KERNEL_LOC_UBUNTU)
    dst_file = "%s/vm_kernel_log" % log_dir
    scp_vm_to_host(credentials, ip, vm_file, dst_file)

    log.info("Collecting dmesg log")
    vm_file = "%s" % (const.DMESG_LOC)
    dst_file = "%s/vm_dmesg_log" % log_dir
    scp_vm_to_host(credentials, ip, vm_file, dst_file)


def get_modified_xml(conf_credentials):
    """
    This function will modify the deafult xml with user provided inputs
    args:
    conf_credentials: Dictionary of user input
    """

    vm_name = conf_credentials.get('name')
    memory = conf_credentials.get('memory')
    num_vcpus = conf_credentials.get('vcpus')
    image_file = conf_credentials.get('image_file')
    mac_address = rand_mac()
    log.info("VM mac is %s", mac_address)
    vm_uuid = uuid.uuid4()
    log.info("vm uuid is %s", vm_uuid)
    # TODO [Make a wrapper for this: Ticket T306]
    tree = et.fromstring(const.DEFAULT_XML)
    tree.find('name').text = vm_name
    tree.find('memory').text = str(memory)
    tree.find('vcpu').text = str(num_vcpus)
    tree.find('uuid').text = str(vm_uuid)
    elem = tree.find('devices/disk/source')
    elem.attrib['file'] = image_file
    elem = tree.find('devices/interface/mac')
    elem.attrib['address'] = mac_address
    modified_xml = et.tostring(tree)
    return modified_xml


def xls_to_csv_converter(xls_filename, csv_filename):
    """
    Converts an Excel file to a CSV file.
    If the excel file has multiple worksheets, only the first worksheet is converted.
    args:
    xls_filename: Filename of xls format
    csv_filename: Filename of csv format
    """
    wb = xlrd.open_workbook(xls_filename)
    sh = wb.sheet_by_index(0)
    fh = open(csv_filename, "wb")
    csv_out = unicodecsv.writer(fh)
    for row_number in xrange(sh.nrows):
        csv_out.writerow(sh.row_values(row_number))
    fh.close()


def create_file(file_name):
    """
    Create a file
    args:
    file_name: Name of file
    """
    log.info("Creating new file %s" % file_name)
    try:
        file = open(file_name, 'a')
        file.close()
    except:
        raise Exception("Cannot create file")


def get_host_arch():
    """
    This function will return the architecture of host
    """
    arch = execute_cmd_output('uname -m')[:-1]
    log.info("Host architecture is %s" % arch)
    return arch


def check_cpu_offline_vm(cpu_number, credentials, ip):
    """
    This function will offline the provided cpu and will make sure it is offline
    by checking in /proc/cpuinfo and /proc/interrupts
    args:
    cpu_number: CPU which needs to be offline
    credentials: Credentials of VM
    ip: IP of VM
    """
    cpu_list = []
    log.info("Making CPU %s offline" % cpu_number)
    cmd = ("echo 0 > /sys/devices/system/cpu/cpu%s/online" % cpu_number)
    output = execute_cmd_vm_output(cmd, credentials, ip, root=True)
    log.info("Checking in /proc/cpuinfo if CPU %s is offline" % cpu_number)
    cmd = ("cat /proc/cpuinfo")
    output = execute_cmd_vm_output(cmd, credentials, ip, root=True)
    for line in output.splitlines():
        if re.search("^processor", line) is not None:
            cpu_list.append((line.split(":")[1]).strip())
    log.info("List of online cpus %s" % cpu_list)
    if cpu_number in cpu_list:
        raise Exception("cpu %s is in /proc/cpuinfo" % cpu_number)
    log.info("CPU %s is not in /proc/cpuinfo" % cpu_number)

    log.info("Checking in /proc/interrrupts if CPU %s is offline" % cpu_number)
    cmd = ("cat /proc/interrupts")
    output = execute_cmd_vm_output(cmd, credentials, ip, root=True)
    cpu_name = "CPU" + cpu_number
    for line in output.splitlines():
        if len(re.findall('\\b' + cpu_name + '\\b', line)) > 0:
            raise Exception("cpu %s is in /proc/interrupts" % cpu_number)
    log.info("%s is not in /proc/interrupts" % cpu_name)


def check_cpu_online_vm(cpu_number, credentials, ip):
    """
    This function will brin provided cpu online and make sure it is online
    by checking in /proc/cpuinfo and /proc/interrupts
    args:
    cpu_number: CPU which needs to be online
    credentials: Credentials of VM
    ip: IP of VM
    """
    cpu_list = []
    log.info("Making CPU %s online" % cpu_number)
    cmd = ("echo 1 > /sys/devices/system/cpu/cpu%s/online" % cpu_number)
    output = execute_cmd_vm_output(cmd, credentials, ip, root=True)
    log.info("Checking in /proc/cpuinfo if CPU %s is online" % cpu_number)
    cmd = ("cat /proc/cpuinfo")
    output = execute_cmd_vm_output(cmd, credentials, ip, root=True)
    for line in output.splitlines():
        if re.search("^processor", line) is not None:
            cpu_list.append((line.split(":")[1]).strip())
    log.info("List of online cpus %s" % cpu_list)
    if cpu_number not in cpu_list:
        raise Exception("cpu %s is not in /proc/cpuinfo" % cpu_number)
    log.info("CPU %s is in /proc/cpuinfo" % cpu_number)

    log.info("Checking in /proc/interrrupts if CPU %s is online" % cpu_number)
    cmd = ("cat /proc/interrupts")
    output = execute_cmd_vm_output(cmd, credentials, ip, root=True)
    cpu_name = "CPU" + cpu_number
    for line in output.splitlines():
        if len(re.findall('\\b' + cpu_name + '\\b', line)) > 0:
            return 0
    raise Exception("cpu %s is not  in /proc/interrupts" % cpu_number)


def copy_vm_image():
    """
    This function will copy VM images in /usr/local
    """
    loc = os.environ['HOME']
    log.info("Copying vm image from %s/images to /usr/local" % loc)
    cmd = ("sudo cp -f %s/images/* /usr/local" % loc)
    output = execute_cmd_output(cmd)


def check_vm_mem(credentials, ip):
    """
    This function will return the mem allocated inside VM in Mb.
    args:
    credentials: Credentials of VM
    ip: IP of VM
    """
    cmd = ("cat /proc/meminfo")
    output = execute_cmd_vm_output(cmd, credentials, ip)
    for line in output.splitlines():
        if "MemTotal" in line:
            mem = (line.split(":")[1].strip()).split(" ")[0]
    memory = int(mem) / int(1024)
    return memory


def check_vm_cpu_num(credentials, ip):
    """
    This gunction will return the number of cpus allocated inside a vm
    """
    cpu_list = []
    cmd = ("cat /proc/cpuinfo")
    output = execute_cmd_vm_output(cmd, credentials, ip, root=True)
    for line in output.splitlines():
        if re.search("^processor", line) is not None:
            cpu_list.append((line.split(":")[1]).strip())
    return len(cpu_list)


def check_dpkg_lock(credentials, ip):
    """
    This function will check for dpkg lock and will remove it.
    args:
    credentials: Credentials of VM
    ip: IP of VM
    """
    cmd = ("export DEBIAN_FRONTEND=noninteractive")
    output = execute_cmd_vm_output(cmd, credentials, ip)
    for i in range(const.RETRY):
        cmd = ("ps aux | grep -e apt -e adept | grep -v grep")
        output = execute_cmd_vm_output(cmd, credentials, ip, check=False)
        if output is None:
            return 0
        time.sleep(2)
    cmd = ("sudo rm /var/lib/dpkg/lock")
    output = execute_cmd_vm_output(cmd, credentials, ip)
    cmd = ("sudo dpkg --configure -a")
    output = execute_cmd_vm_output(cmd, credentials, ip)
    cmd = ("sudo apt-get clean")
    output = execute_cmd_vm_output(cmd, credentials, ip)


def check_vm_health(credentials, ip):
    """
    This function will check the health of VM by checking number of vcpus
    memory detail and drives information
    args:
    credentials: Credentials of VM
    ip: IP of VM
    """
    cmd = ("free -g | grep -v Swap")
    output = execute_cmd_vm_output(cmd, credentials, ip)
    log.info("System memory status is %s" % output)
    num_cpus = check_vm_cpu_num(credentials, ip)
    log.info("Number of vcpus present in VM are %s" % num_cpus)
    cmd = ("lsblk --noheadings | grep disk")
    execute_cmd_vm_output(cmd, credentials, ip, root=False)
    devices = output.strip()
    log.info("Devices present inside VM are %s " % devices)
    if get_host_arch() == "x86_64":
        cmd = "dmesg -T --level=err"
        output = execute_cmd_vm_output(cmd, credentials, ip, root=False)
        # Raise exception on any error found
        errors = output.split("\n")
        if output:
            for error in errors:
                if error and "kvm" not in error:
                    raise Exception("VM kernel returned following errors:\n%s" % error)


def clear_vm_snapshots():
    """
    This function will remove all previously created VM image snapshots
    """
    output = execute_cmd_output("rm -f %s*.qcow2" % const.VM_FILES_DIR)


def prepare_vm_snapshots(total_vm, vm_args):
    """
    This function will create as many VM snapshots as required by total_vm
    args:
    total_vm: total vms required to be created by the test
    vm_args: part of test arguments, used to get 'disk' field defined in conf.yaml
    """
    # Clear old VM snapshots
    clear_vm_snapshots()
    for i in xrange(total_vm):
        # Get image path from test arguments
        img_path = vm_args.get('disk').split(',')[0].split('=')[1]
        # Execute command
        output = execute_cmd_output("qemu-img create -b %s -f qcow2 %s%s.qcow2" % (img_path,
                                                                                   const.VM_FILES_DIR,
                                                                                   "test" + str(i)
                                                                                   )
                                    )


def create_tap_on_host(tap_type='default', tap_ifname='tap0', bridge_name='br0',
                       eth_ifname='eth0', ip=const.TAP_DEFAULT_IP):
    """
    This function will create tap interface on host
    This function will return True if external tap interface was created else it will return False
    args:
    tap_type: type of tap interface to create; default, host-only, external
    tap_ifname: name of tap interface specified by user
    bridge_name: name of bridge interface specified by user
    eth_ifname: name of wired ethernet interface specified by user
    ip: host IP in case of host only tap interface
    """
    # Create tap interface
    if "Ubuntu" in platform.platform() or "SuSE" in platform.platform():
        cmd = "sudo tunctl -t %s" % tap_ifname
    elif "centos" in platform.platform():
        cmd = "sudo ip tuntap add %s mode tap" % tap_ifname
    else:
        cmd = ""
    output = execute_cmd_output(cmd)
    # Create bridge interface
    output = execute_cmd_output("sudo brctl addbr %s" % bridge_name)
    # Add tap interface to bridge
    output = execute_cmd_output("sudo brctl addif %s %s" % (bridge_name, tap_ifname))
    # Enable tap interface
    output = execute_cmd_output("sudo ifconfig %s promisc up" % tap_ifname)
    if tap_type == 'external':
        # Add wired interface to bridge
        output = execute_cmd_output("sudo brctl addif %s %s" % (bridge_name, eth_ifname))
        # Enable wired interface
        output = execute_cmd_output("sudo ifconfig %s promisc up" % eth_ifname)
        # run DHCP on bridge
        output = execute_cmd_output("sudo dhclient %s" % bridge_name)
        return True
    else:
        if tap_type == 'host_only':
            # Assign bridge a static IP and enable it
            output = execute_cmd_output("sudo ifconfig %s %s up" % (bridge_name, ip))
        else:
            # Enable bridge interface
            output = execute_cmd_output("sudo ifconfig %s up" % bridge_name)
        return False


def destroy_tap_on_host(tap_type='default', bridge_name='br0', eth_ifname='eth0', tap_ifname='tap0'):
    """
    This function removes tap and bridge interface and
    assigns an IP to wire interface in-case of external tap interface
    args:
    tap_type: type of tap interface to create; default, host-only, external
    bridge_name: name of bridge interface specified by user
    eth_ifname: name of wired ethernet interface specified by user
    """
    # Disable bridge interface
    output = execute_cmd_output("sudo ip link set %s down" % bridge_name)
    if tap_type is 'external':
        output = execute_cmd_output("sudo brctl delif %s %s" % (bridge_name, eth_ifname))
    # Remove bridge interface
    output = execute_cmd_output("sudo brctl delbr %s" % bridge_name)
    # Run DHCP on wired interface in-case of external tap interface
    if tap_type is 'external':
        output = execute_cmd_output("sudo dhclient %s" % eth_ifname)
    if "centos" in platform.platform():
        execute_cmd('sudo ip link set %s down' % tap_ifname)
        execute_cmd('sudo ip link delete %s' % tap_ifname)


def check_host_health(start, stop):
    """
    This function checks for any errors in kernel log during test
    args:
    start: start time of test
    stop: stop time of test
    """
    # Check kernel log for any error between start and stop
    output = execute_cmd_output("dmesg -T --level=err"
                                " | "
                                "awk '$4 >= \"%s\" && $4 <= \"%s\"'" % (start, stop))
    # Raise exception on any error found
    errors = output.split("\n")
    if output:
        for error in errors:
            if error and "kvm" not in error:
                raise Exception("Host kernel returned following errors\n%s" % error)


def get_vm_telnet_port(handle):
    """
    This function returns the telnet port assigned to the VM serial interface
    args:
    handle: libvirt object that holds information about VM
    """
    raw_xml = handle.XMLDesc()
    xml = minidom.parseString(raw_xml)
    serial_tags = xml.getElementsByTagName('serial')
    for item in serial_tags:
        source_tag = item.childNodes
        for tag in source_tag:
            if tag.nodeName[0:1] != '#':
                for attr in tag.attributes.keys():
                    if tag.attributes[attr].name == 'service':
                        return tag.attributes[attr].value


def execute_cmd_vm_telnet(handle, cmd, timeout=1200):
    """
    This function executes bash command on VM via telnet
    args:
    handle: VM handle
    cmd: bash command
    """
    host = const.TELNET_HOST
    port = int(get_vm_telnet_port(handle))
    if port is None:
        raise Exception("Cannot open telnet session with %s VM" % handle.name())
    # Open telnet session with VM
    tn = telnetlib.Telnet(host, port)
    tn.write(cmd + "\r\n")
    try:
        output = tn.read_until(const.VM_PROMPT, timeout=timeout)
    except ValueError:
        raise Exception("Command %s failed to execute on guest" % cmd)
    if const.VM_PROMPT not in output:
        raise Exception("Telnet command %s timed out" % cmd)
    # Close telnet session
    tn.close()
    result = "\n".join((output.split("\n"))[:-1])
    return result


def exe_command_vm(cmd, credentials=None, ip=None, domain=None, root=False, check=True, timeout=300):
    """
    This function executes bash command on VM
    args:
    credentials: Credentials of guest
    ip: IP of guest
    cmd: bash command
    """
    if domain is not None:
        output = execute_cmd_vm_telnet(domain, cmd, timeout=timeout)
    else:
        output = execute_cmd_vm_output(cmd, credentials, ip, root=root, check=check)
    return output


def suppress_kvm_kernel_error():
    cmd = "echo 1 > /sys/module/kvm/parameters/ignore_msrs"
    execute_cmd(cmd)


def get_vm_net_ifname(handle):
    """
    args:
    handle: handle of VM
    """
    for i in range(const.RETRY):
        try:
            ifaces = handle.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        except:
            pass
        else:
            for (name, val) in ifaces.iteritems():
                if name != "lo":
                    return name
