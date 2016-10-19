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
Test cases for ovs_vsctl.parser.
"""

import logging
import unittest

from nose.tools import eq_

from ovs_vsctl.parser import Record

LOG = logging.getLogger(__name__)


class TestRecord(unittest.TestCase):
    """
    Test cases for ovs_vsctl.parser.Record.
    """

    def test_str(self):
        record = Record(aaa=1, bbb='value')

        eq_("Record(aaa=1, bbb='value')", str(record))
