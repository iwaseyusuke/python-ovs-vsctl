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
Parsers for 'ovs-vsctl' command outputs.
"""

import json

from ovs_vsctl.utils import is_valid_uuid


def line_parser(buf):
    """
    Parses the given `buf` as str representation of list of values
    (e.g. 'ovs-vsctl list-br' command).

    :param buf: str type value containing values list.
    :return:  list of parsed values.
    """
    values = []
    for line in buf.split('\n'):
        if line:
            values.append(line.strip())
    return values


def show_cmd_parser(buf):
    """
    Parser for 'ovs-vsctl show' command.

    Currently, parses ONLY 'ovs_version' column.

    :param buf: str type output of 'ovs-vsctl show' command.
    :return: dict type value of 'ovs-vsctl show' command.
    """
    outputs = {}
    for line in line_parser(buf):
        if line.startswith('ovs_version'):
            # e.g.)
            #   ovs_version: "2.5.0"
            outputs['ovs_version'] = line.split('"')[1]

    return outputs


def _record_row_parser(buf):
    """
    Parses the given `buf` as str representation of 'row' into `column`
    and `value`.

    Additionally, strips leading and trailing whitespace characters.

    `buf` should be formatted in::

         '<column> : <value>'

    Example::

        'name                : "br1"'

    :param buf: single row in str type.
    :return: tuple of `column` and `value`.
    """
    column, value = buf.split(':', 1)

    return column.strip(), value.strip()


def _record_value_parser(buf):
    """
    Parses value within OVSDB tables and returns python object corresponding
    to the value type.

    :param buf: value of 'ovs-vsctl list' or `ovs-vsctl find` command.
    :return: python object corresponding to the value type of row.
    """
    if buf.startswith('["uuid",'):
        # UUID type
        # e.g.)
        #   ["uuid","79c26f92-86f9-485f-945d-5786c8147f53"]
        _, value = json.loads(buf)
    elif buf.startswith('["set",'):
        # Set type
        # e.g.)
        #   ["set",[100,200]]
        _, value = json.loads(buf)
    elif buf.startswith('["map",'):
        # Map type
        # e.g.)
        #   ["map",[["stp-enable","true"]]]
        _, value = json.loads(buf)
        value = dict(value)
    else:
        # Other type
        # e.g.)
        #   "br1"       --> str
        #   100         --> int
        #   true/false  --> True/False
        #   null  ...   --> None
        value = json.loads(buf)

    return value


class Record():  # pylint: disable=too-few-public-methods
    """
    Record object of OVSDB table.

    Attributes are corresponding to columns of parsed tables.
    """

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    @classmethod
    def parse(cls, buf):
        """
        Parses the given `buf` as str containing a record of rows.

        :param buf: Record in str type.
        :return: `Record` instance.
        """
        kwargs = {}

        # Splits buf containing the record info into rows
        for row in buf.split('\n'):
            # Skips empty.
            if not row:
                continue

            column, value = _record_row_parser(row)
            value = _record_value_parser(value)
            kwargs[column] = value

        return cls(**kwargs)

    def __repr__(self):
        def _sort(items):
            return sorted(items, key=lambda x: x[0])

        return ('%s(' % self.__class__.__name__
                + ', '.join(['%s=%s' % (k, repr(v))
                             for k, v in _sort(self.__dict__.items())]) + ')')

    __str__ = __repr__


def list_cmd_parser(buf):
    """
    Parser for 'ovs-vsctl list' and 'ovs-vsctl find' command.

    `buf` must be the str type and the output of 'ovs-vsctl list' or
    ovs-vsctl find' command with '--format=list' and '--data=json' options.

    :param buf: str type output of 'ovs-vsctl list' command.
    :return: list of `Record` instances.
    """
    records = []

    # Assumption: Each record is separated by empty line.
    for record in buf.split('\n\n'):
        records.append(Record.parse(record))

    return records


find_cmd_parser = list_cmd_parser  # pylint: disable=invalid-name


def get_cmd_parser(buf):
    """
    Parser for 'ovs-vsctl get' command.

    `buf` must be the str type and the output of 'ovs-vsctl get' command.

    Assumption: The output is mostly formatted in json, except for 'uuid'
    and 'key' of map type value.

    :param buf: value of 'ovs-vsctl get' command.
    :return: python object corresponding to the value type of row.
    """
    buf = buf.strip('\n')
    try:
        value = json.loads(buf)
        return value
    except ValueError:
        # Handles in the following.
        pass

    value = buf  # Default value
    if is_valid_uuid(buf):
        # UUID type
        pass  # Uses the default
    elif buf.startswith('['):
        # Set type (might be containing UUIDs)
        # e.g.)
        #   [<UUID>, <UUID>]
        buf = buf.replace('[', '["').replace(', ', '", "').replace(']', '"]')
        value = json.loads(buf)
    elif buf.startswith('{'):
        # Map type
        # e.g.)
        #   {stp-enable="true", stp-priority="100"}
        buf = buf.replace('{', '{"').replace('=', '": ').replace(', ', ', "')
        value = json.loads(buf)

    return value
