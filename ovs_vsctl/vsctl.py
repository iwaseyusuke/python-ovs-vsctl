# Copyright (C) 2016 Iwase Yusuke <iwase yusuke0 at gmail com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
APIs for execute 'ovs-vsctl' command.
"""

# pylint: disable=no-name-in-module,import-error
from distutils.spawn import find_executable
# pylint: enable=no-name-in-module,import-error
import shlex
from os import path

import netaddr

from ovs_vsctl import exception
from ovs_vsctl import utils


INSTALLED_OVS_VSCTL = find_executable("ovs-vsctl")
DEFAULT_OVS_VSCTL = '%s/bin/ovs-vsctl' % path.dirname(__file__)


class VSCtl(object):
    """
    Runner class for 'ovs-vsctl' command.

    :param protocol: `'tcp'`, `'ssl'`, and `'unix'` are available.
    :param addr: IP address of switch to connect.
    :param port: (TCP or SSL) port number to connect.
    :raise: * ValueError -- When the given parameter is invalid.
    """
    SUPPORTED_PROTOCOLS = ['tcp', 'ssl', 'unix']
    SUPPORTED_FORMATS = ['json']

    def __init__(self, protocol='tcp', addr='127.0.0.1', port=6640):
        # Validates the given protocol.
        if protocol not in self.SUPPORTED_PROTOCOLS:
            raise ValueError('Unsupported protocol: %s' % protocol)
        self.protocol = protocol

        # Validates the given IP address.
        if (not self.protocol == "unix" and not netaddr.valid_ipv4(addr)
                and not netaddr.valid_ipv6(addr)):
            raise ValueError('Invalid IP address: %s' % addr)
        self.addr = addr

        # Validates the given port number.
        try:
            self.port = int(str(port), 0)
        except ValueError:
            raise ValueError('Invalid (TCP or SSL) port number: %s' % port)

        # If "ovs-vsctl" executable not found, uses the built-in binary.
        self.ovs_vsctl_path = INSTALLED_OVS_VSCTL or DEFAULT_OVS_VSCTL

    @property
    def ovsdb_addr(self):
        """
        Returns OVSDB server address formatted like '--db' option of
        'ovs-vsctl' command.

        Example::

            >>> from ovs_vsctl import VSCtl
            >>> vsctl = VSCtl('tcp', '127.0.0.1', 6640)
            >>> vsctl.ovsdb_addr
            'tcp:127.0.0.1:6640'

        :return: OVSDB server address.
        """
        if self.protocol == 'unix':
            return '%s:%s'      % (self.protocol, self.addr)
        elif ':' in self.addr:
            # If ip is an IPv6 address, then wrap ip with square brackets.
            return '%s:[%s]:%d' % (self.protocol, self.addr, self.port)
        else:
            return '%s:%s:%d' % (self.protocol, self.addr, self.port)

    def run(self, command, table_format='list', data_format='string',
            parser=None):
        """
        Executes ovs-vsctl command.

        `command` is an str type and the format is the same as 'ovs-vsctl`
        except for omitting 'ovs-vsctl' in command format.

        For example, if you want to get the list of ports, the command
        for 'ovs-vsctl' should like 'ovs-vsctl list port' and `command`
        argument for this method should be::

            >>> from ovs_vsctl import VSCtl
            >>> vsctl = VSCtl('tcp', '127.0.0.1', 6640)
            >>> vsctl.run(command='list port')
            <subprocess.Popen object at 0x7fbbe9d549e8>

        :param command: Command to execute.
        :param table_format: Table format. Meaning is the same as '--format'
         option of 'ovs-vsctl' command.
        :param data_format: Cell format in table. Meaning is the same as
         '--data' option of 'ovs-vsctl' command.
        :param parser: Parser class for the outputs. If this parameter is
         specified `table_format` and `data_format` is overridden with
         `table_format='list'` and `data_format='json'`.
        :return: Output of 'ovs-vsctl' command. If `parser` is not specified,
         returns an instance of 'subprocess.Popen'. If `parser` is specified,
         the given `parser` is applied to parse the outputs.
        :raise: * ovs_vsctl.exception.VSCtlCmdExecError -- When the given
                  command fails.
                * ovs_vsctl.exception.VSCtlCmdParseError -- When the given
                  parser fails to parse the outputs.
        """
        # Constructs command.
        args = [
            self.ovs_vsctl_path,
            '--db=%s' % self.ovsdb_addr,
        ]
        if parser:
            table_format = 'list'
            data_format = 'json'
        args.extend([
            '--format=%s' % table_format,
            '--data=%s' % data_format,
        ])
        args.extend(shlex.split(command))

        # Executes command.
        process = utils.run(args)
        if process.returncode != 0:
            raise exception.VSCtlCmdExecError(process.stderr.read())

        # If parser is specified, applies parser and returns it.
        if parser:
            try:
                return parser(process.stdout.read())
            except Exception as e:  # pylint: disable=invalid-name
                raise exception.VSCtlCmdParseError(e)

        # Returns outputs in str type.
        return process
