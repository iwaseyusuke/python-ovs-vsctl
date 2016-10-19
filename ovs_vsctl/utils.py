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
Utilities.
"""

from subprocess import PIPE
from subprocess import Popen
from uuid import UUID


def run(args):
    """
    Wrapper of 'subprocess.run'.

    :param args: Command arguments to execute.
    :return: instance of 'subprocess.Popen'.
    """
    popen = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    popen.wait()

    return popen


def is_valid_uuid(uuid):
    """
    Returns `True` if the given `uuid` is valid, otherwise returns `False`.

    :param uuid: str type value to be validated.
    :return: `True` if valid, else `False`.
    """
    try:
        UUID(uuid)
    except ValueError:
        return False
    return True
