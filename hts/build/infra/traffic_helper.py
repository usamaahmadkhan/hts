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
import random
sys.path.insert(0, "/opt/hts/")
from subprocess import call
from infra import helper
from infra import const
log = logging.getLogger('test' + '.' + __name__)


def run_iperf(cli_cmd, credentials, iperf_server, iperf_client, telnet):
    """
    This function will run iperf tcp client command and will check for result
    args:
    cli_cmd: iperf client command
    credentials: credentails of vm
    iperf_server: iperf server IP
    iperf_client: iperf client IP
    telnet: Flag for executing command whteher through telnet or ssh
    """
    retry_cnt = 0
    while (retry_cnt < 3):
        log.info("Running iperf client on %s" % iperf_client)
        log.info("Running iperf client command %s" % cli_cmd)
        if not credentials:
            result = helper.execute_cmd_output(cli_cmd)
        else:
            if telnet:
                result = helper.execute_cmd_vm_telnet(credentials, cli_cmd)
            else:
                result = helper.execute_cmd_vm_output(cli_cmd, credentials, iperf_client, root=True)

        if "Connection refused" not in result:
            break
        retry_cnt += 1
        if retry_cnt < 3:
            log.info("iperf retry %d failed. Sleeping and trying again.", retry_cnt)
            time.sleep(5)
    output = result.split()
    log.info("Output of client command %s" % output)
    bandwidth_value = output[-2] + " " + output[-1]
    for line in output:
        if ((line == "Kbits/sec") or (line == "Mbits/sec") or
           (line == "Gbits/sec")):
            return bandwidth_value
    raise Exception("Iperf session failed")


def run_iperf_udp(cli_cmd, credentials, iperf_server, iperf_client, telnet):
    """
    This function will run iperf udp client command and will check for result
    args:
    cli_cmd: iperf client command
    credentials: credentails of vm
    iperf_server: iperf server IP
    iperf_client: iperf client IP
    telnet: Flag for executing command whteher through telnet or ssh
    """
    retry_cnt = 0
    while (retry_cnt < 3):
        log.info("Running iperf client on %s" % iperf_client)
        log.info("Running iperf client command %s" % cli_cmd)
        if not credentials:
            result = helper.execute_cmd_output(cli_cmd)
        else:
            if telnet:
                result = helper.execute_cmd_vm_telnet(credentials, cli_cmd)
            else:
                result = helper.execute_cmd_vm_output(cli_cmd, credentials, iperf_client, root=True)

        if "Connection refused" not in result:
            break
        retry_cnt += 1
        if retry_cnt < 3:
            log.info("iperf retry %d failed. Sleeping and trying again.", retry_cnt)
            time.sleep(5)
    output = result.split()
    log.info("Output of client command %s" % output)
    for line in output:
        if "WARNING" in line:
            result = "FAILED"
        if (result == "FAILED"):
            raise Exception("Iperf session failed")
    return 0


def validate_iperf(server_credentials, iperf_server, client_credentials, iperf_client, length_list, parallel=False,
                   port=const.IPERF_PORT, run_time=10, telnet=False):
    """
    This function will validate iperf tcp session.
    args:
        credentials: credentails of vm
    iperf_server: iperf server IP
    iperf_client: iperf client IP
    length_list: List of length to be used
    parallel: Flag for parallel connection
    port: Port to be used
    run_time: Time for ip[erf session
    telnet: Flag for executing command whteher through telnet or ssh
    """
    log.info("Running iperf server on %s" % iperf_server)
    if not server_credentials:
        output = helper.execute_cmd_output(const.IPERF_SVR_CMD)
    else:
        if telnet:
            output = helper.execute_cmd_vm_telnet(server_credentials, const.IPERF_SVR_CMD)
        else:
            output = helper.execute_cmd_vm_output(const.IPERF_SVR_CMD, server_credentials, iperf_server, root=True)

    bandwidth_list = []
    if parallel:
        cmd = ("iperf -c %s -P %s -p %s -t %s" % (iperf_server, parallel, port, run_time))
        bandwidth = run_iperf(cmd, client_credentials, iperf_server, iperf_client, telnet)
        bandwidth_list.append(bandwidth)
    else:
        for i in length_list:
            cmd = ("iperf -c %s -l %s -p %s -t %s" % (iperf_server, i, port, run_time))
            bandwidth = run_iperf(cmd, client_credentials, iperf_server, iperf_client, telnet)
            bandwidth_list.append(bandwidth)
    log.info("bandwidth list is %s" % bandwidth_list)
    return bandwidth_list


def validate_iperf_udp(server_credentials, iperf_server, client_credentials, iperf_client, length_list,
                       udp_bandwidth, parallel=False, port=5001, run_time=10, telnet=True):
    """
    This function will validate iperf udp session.
    args:
        credentials: credentails of vm
    iperf_server: iperf server IP
    iperf_client: iperf client IP
    length_list: List of length to be used
    parallel: Flag for parallel connection
    port: Port to be used
    run_time: Time for ip[erf session
    telnet: Flag for executing command whteher through telnet or ssh
    """
    log.info("Running iperf server on %s" % iperf_server)
    if not server_credentials:
        output = helper.execute_cmd_output(const.IPERF_SVR_CMD_UDP)
    else:
        if telnet:
            output = helper.execute_cmd_vm_telnet(server_credentials, const.IPERF_SVR_CMD_UDP)
        else:
            output = helper.execute_cmd_vm_output(const.IPERF_SVR_CMD_UDP, server_credentials, iperf_server, root=True)

    if parallel:
        cmd = ("iperf -c %s -u -b %s -P %s -p %s -t %s" % (iperf_server, udp_bandwidth, parallel, port, run_time))
        run_iperf_udp(cmd, client_credentials, iperf_server, iperf_client, telnet)
    else:
        for i in length_list:
            cmd = ("iperf -c %s -u -b %s -l %s -p %s -t %s" % (iperf_server, udp_bandwidth, i, port, run_time))
            run_iperf_udp(cmd, client_credentials, iperf_server, iperf_client, telnet)
