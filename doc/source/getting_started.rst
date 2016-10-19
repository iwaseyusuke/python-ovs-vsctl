Getting Started
===============

Installation
------------

Currently, only installing from GitHub via pip is supported.

.. code-block:: bash

    $ pip install git+https://github.com/iwaseyusuke/python-ovs-vsctl.git


Basic Usage
-----------

``python-ovs-vsctl`` sends OVSDB requests via TCP or SSH connections to
switches.
Please make sure that the manager targets are configured on the switches
before calling the APIs of ``python-ovs-vsctl`` as following.

.. code-block:: bash

    $ sudo ovs-vsctl set-manager ptcp:6640


.. Note::

    The port 6640 is the IANA registered port for OVSDB.


Then, let's call the APIs for OVSDB.

.. code-block:: python

    >>> from ovs_vsctl import VSCtl
    >>> vsctl = VSCtl('tcp', '127.0.0.1', 6640)
    >>> vsctl.run(command='show')
    <subprocess.Popen object at 0x7fd4e86688d0>


Also, you can print the outputs like ``ovs-vsctl`` command.

.. code-block:: python

    >>> popen = vsctl.run('show')
    >>> print(popen.stdout.read())
    77a5cb2b-6a99-449b-adbe-19cfc41ef103
        Manager "ptcp:6640"
        Bridge "s1"
            Controller "ptcp:6634"
            Controller "tcp:127.0.0.1:6633"
            fail_mode: secure
            Port "s1-eth1"
                Interface "s1-eth1"
            Port "s1"
                Interface "s1"
                    type: internal
            Port "s1-eth2"
                Interface "s1-eth2"
        ovs_version: "2.5.0"


But, this format is not convenient for Python programming...
If we can get the outputs as json loaded object, it is more useful, isn't it?

To parse the outputs, you can use the ``ovs-vsctl`` command parsers.

.. code-block:: python

    >>> from ovs_vsctl import list_cmd_parser
    >>> vsctl.run('list port', parser=list_cmd_parser)
    [Record(_uuid='91c8423c-f032-4e0f-a3e2-9e80bddcd5aa', bond_active_slave=[], bond_downdelay=0, bond_fake_iface=False, bond_mode=[], bond_updelay=0, external_ids={}, fake_bridge=False, interfaces='59a88084-fb01-4d0f-b413-0905336e5957', lacp=[], mac=[], name='s1-eth1', other_config={}, qos=[], rstp_statistics={}, rstp_status={}, statistics={}, status={}, tag=[], trunks=[], vlan_mode=[]), Record(_uuid='99f9d4a5-948d-4ed6-9b4c-4d64ada88e5a', bond_active_slave=[], bond_downdelay=0, bond_fake_iface=False, bond_mode=[], bond_updelay=0, external_ids={}, fake_bridge=False, interfaces='8df33dba-cb3b-4d72-891a-9591f2d1e115', lacp=[], mac=[], name='s1', other_config={}, qos=[], rstp_statistics={}, rstp_status={}, statistics={}, status={}, tag=[], trunks=[], vlan_mode=[]), Record(_uuid='ba7fee67-2e97-470a-9df5-446d72fa1645', bond_active_slave=[], bond_downdelay=0, bond_fake_iface=False, bond_mode=[], bond_updelay=0, external_ids={}, fake_bridge=False, interfaces='bab7f26e-be1e-431c-bd99-27fed50c94c5', lacp=[], mac=[], name='s1-eth2', other_config={}, qos=[], rstp_statistics={}, rstp_status={}, statistics={}, status={}, tag=[], trunks=[], vlan_mode=[])]


``list_cmd_parser`` parses the outputs into the list of ``Record`` object
which contain the information of record of OVSDB table.

For more details of the APIs of ``python-ovs-vsctl``, please refer to
the API Reference of this documentation.
