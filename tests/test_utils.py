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
Test cases for ovs_vsctl.utils.
"""

import logging
import unittest

from nose.tools import eq_
from nose.tools import ok_

from ovs_vsctl import utils

LOG = logging.getLogger(__name__)


class TestUtils(unittest.TestCase):
    """
    Test cases for ovs_vsctl.utils.
    """

    def test_is_valid_uuid_with_valid_uuid(self):
        ok_(utils.is_valid_uuid('6925fb19-afe6-43e1-97f0-59bdcba86459'))

    def test_is_valid_uuid_with_invalid_uuid(self):
        eq_(False, utils.is_valid_uuid('xxx'))
