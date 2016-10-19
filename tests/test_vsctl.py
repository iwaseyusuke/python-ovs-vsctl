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
Test cases for ovs_vsctl.vsctl.
"""

import logging
import unittest

from nose.tools import eq_
from nose.tools import raises
from six.moves import mock

from ovs_vsctl.vsctl import VSCtl
from ovs_vsctl.exception import VSCtlCmdExecError
from ovs_vsctl.exception import VSCtlCmdParseError


LOG = logging.getLogger(__name__)


class TestVSCtl(unittest.TestCase):
    """
    Test cases for ovs_vsctl.vsctl.VSCtl.
    """

    @raises(ValueError)
    def test_init_with_invalid_protocol(self):
        VSCtl(protocol='protocol')

    @raises(ValueError)
    def test_init_with_invalid_ip_addr(self):
        VSCtl(ip_addr='xxx.xxx.xxx.xxx')

    @raises(ValueError)
    def test_init_with_invalid_port(self):
        VSCtl(port='xxx')

    def test_ovsdb_addr_ipv4(self):
        vsctl = VSCtl(protocol='tcp', ip_addr='127.0.0.1', port=6640)

        eq_('tcp:127.0.0.1:6640', vsctl.ovsdb_addr)

    def test_ovsdb_addr_ipv6(self):
        vsctl = VSCtl(protocol='tcp', ip_addr='::1', port=6640)

        eq_('tcp:[::1]:6640', vsctl.ovsdb_addr)

    @raises(VSCtlCmdExecError)
    @mock.patch('ovs_vsctl.utils.run')
    def test_run_cmd_exec_error(self, mock_run):
        mock_process = mock.MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process

        vsctl = VSCtl(protocol='tcp', ip_addr='127.0.0.1', port=6640)
        vsctl.run('show')

    @raises(VSCtlCmdParseError)
    @mock.patch('ovs_vsctl.utils.run')
    def test_run_cmd_parse_error(self, mock_run):
        mock_process = mock.MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        mock_parser = mock.MagicMock(
            side_effect=VSCtlCmdExecError('Expected Error'))

        vsctl = VSCtl(protocol='tcp', ip_addr='127.0.0.1', port=6640)
        vsctl.run('show', parser=mock_parser)

    @mock.patch('ovs_vsctl.utils.run')
    def test_run_with_no_parse(self, mock_run):
        mock_popen = mock.MagicMock()
        mock_popen.returncode = 0
        mock_run.return_value = mock_popen

        vsctl = VSCtl(protocol='tcp', ip_addr='127.0.0.1', port=6640)
        output = vsctl.run('show', parser=None)

        eq_(mock_popen, output)
