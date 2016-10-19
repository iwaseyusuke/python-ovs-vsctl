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
Test cases for APIs using Docker.
"""

from distutils.spawn import find_executable
import logging
import shlex
import unittest
from uuid import UUID

from nose.tools import eq_
from nose.tools import ok_

from ovs_vsctl import VSCtl
from ovs_vsctl import line_parser
from ovs_vsctl import show_cmd_parser
from ovs_vsctl import list_cmd_parser
from ovs_vsctl import get_cmd_parser
from ovs_vsctl.parser import Record
from ovs_vsctl.utils import run


LOG = logging.getLogger(__name__)

DOCKER_IMAGE_MININET = 'mininet'

OVSDB_PORT = 6640


def setUpModule():
    if not find_executable('docker'):
        raise unittest.SkipTest(
            'Docker is not available. Test in %s will be skipped.' % __name__)


def _run(command):
    return run(shlex.split(command)).stdout.read().split('\n')


class TestAPIs(unittest.TestCase):
    """
    Test cases for ovs_vsctl.
    """
    vsctl = None  # instance of ovs_vsctl.VSCtl

    @classmethod
    def _docker_exec(cls, container, command):
        return _run('docker exec -t -i %s %s' % (container, command))

    @classmethod
    def _docker_exec_mn(cls, command):
        return cls._docker_exec('mininet', command)

    @classmethod
    def _docker_run(cls, name, image):
        return _run('docker run --name %s -t -d %s' % (name, image))[0]

    @classmethod
    def _docker_stop(cls, container):
        return _run('docker stop %s' % container)[0]

    @classmethod
    def _docker_rm(cls, container):
        return _run('docker rm %s' % container)[0]

    @classmethod
    def _docker_inspect_ip_addr(cls, container):
        return _run(
            'docker inspect --format="{{.NetworkSettings.IPAddress}}" %s' %
            container)[0]

    @classmethod
    def setUpClass(cls):
        cls._docker_run('mininet', DOCKER_IMAGE_MININET)
        mininet_ip = cls._docker_inspect_ip_addr('mininet')
        # Note: Waits for OVS starting up.
        _run('sleep 10')

        cls._docker_exec_mn(
            'ovs-vsctl add-br s1')
        cls._docker_exec_mn(
            'ovs-vsctl add-port s1 s1-eth1')
        cls._docker_exec_mn(
            'ovs-vsctl add-port s1 s1-eth2')
        cls._docker_exec_mn(
            'ovs-vsctl set Port s1 tag=100')
        cls._docker_exec_mn(
            'ovs-vsctl set Port s1 trunks=100,200')
        cls._docker_exec_mn(
            'ovs-vsctl set Port s1 other_config:stp-enable=true')

        cls.vsctl = VSCtl('tcp', mininet_ip, OVSDB_PORT)

    @classmethod
    def _tear_down_mn_container(cls):
        cls._docker_exec_mn('mn --clean')
        cls._docker_stop('mininet')
        cls._docker_rm('mininet')

    @classmethod
    def tearDownClass(cls):
        cls._tear_down_mn_container()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_line_parser(self):
        output = self.vsctl.run('list-ports s1', parser=line_parser)

        eq_(['s1-eth1', 's1-eth2'], output)

    def test_show_cmd_parser(self):
        output = self.vsctl.run('show', parser=show_cmd_parser)

        eq_({'ovs_version': '2.5.0'}, output)

    def test_list_cmd_parser(self):
        output = self.vsctl.run('list Port s1', parser=list_cmd_parser)

        eq_(1, len(output))
        ok_(isinstance(output[0], Record))
        eq_('s1', output[0].name)

    def test_get_cmd_parser_with_json_value(self):
        output = self.vsctl.run('get Port s1 tag', parser=get_cmd_parser)

        eq_(100, output)

    def test_get_cmd_parser_with_uuid(self):
        output = self.vsctl.run('get Port s1 _uuid', parser=get_cmd_parser)

        ok_(UUID(output))

    def test_get_cmd_parser_with_uuid_list(self):
        output = self.vsctl.run(
            'get Port s1 interfaces', parser=get_cmd_parser)

        ok_(isinstance(output, list))
        ok_(UUID(output[0]))

    def test_get_cmd_parser_with_map(self):
        output = self.vsctl.run(
            'get Port s1 other_config', parser=get_cmd_parser)

        eq_({'stp-enable': 'true'}, output)
