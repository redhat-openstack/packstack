#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import contextlib
import inspect
import os
import random
import subprocess
import sys
import tempfile
import uuid
import unittest


def execute(cmd_string, check_error=True, return_code=0, input=None,
            block=True, error_msg='Error executing cmd'):
    print(cmd_string)
    cmd = cmd_string.split(' ')
    proc = subprocess.Popen(cmd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if input:
        proc.communicate(input=input)
    elif block:
        proc.wait()
    if (check_error and
            proc.returncode is not None and
            proc.returncode != return_code):
        msg = """
%(error_msg)s
 Command: %(cmd)s
 Exit Code: %(code)s
""".strip() % dict(cmd=' '.join(cmd),
                   code=proc.returncode,
                   error_msg=error_msg)
        if input:
            msg += "\n Stdin: %s" % input
        if not proc.stdout.closed:
            msg += "\n Stdout: %s" % proc.stdout.read()
        if not proc.stderr.closed:
            msg += "\n Stderr: %s" % proc.stderr.read()
        raise Exception(msg)
    return proc


def e(cmd, prefix='ip netns exec ', sudo=False, **kwargs):
    frame_locals = inspect.getargvalues(sys._getframe(1))[3]
    if sudo:
        prefix = 'sudo ' + prefix
    return execute(prefix + cmd % frame_locals, **kwargs)


def rand_name(name='test'):
    return '%s-%s' % (name, str(random.randint(1, 0x7fffffff)))


@contextlib.contextmanager
def add_namespace():
    name = rand_name('testns')
    try:
        e('ip netns add %(name)s', prefix='')
        e('%(name)s ip link set lo up')
        yield name
    finally:
        e('ip netns delete %(name)s', prefix='')


@contextlib.contextmanager
def add_namespaces():
    with add_namespace() as ns1:
        with add_namespace() as ns2:
            yield ns1, ns2


def add_veth_pair(ns1, ns2, veth1, veth2, address1, address2):
    e('ip link add %(veth1)s netns %(ns1)s type veth '
      'peer name %(veth2)s netns %(ns2)s', prefix='')
    e('%(ns1)s ip link show %(veth1)s')
    e('%(ns2)s ip link show %(veth2)s')
    e('%(ns1)s ip -4 addr add %(address1)s/24 brd 255.255.255.0 '
      'scope global dev %(veth1)s')
    e('%(ns2)s ip -4 addr add %(address2)s/24 brd 255.255.255.0 '
      'scope global dev %(veth2)s')
    e('%(ns1)s ip link set %(veth1)s up')
    e('%(ns2)s ip link set %(veth2)s up')


class TestNetns(unittest.TestCase):

    def test_neutron_netns_cmds(self):
        """Exercise the netns functionality required by neutron.

          - Check that a veth pair can be configured to transit traffic
            between 2 namespaces
          - Check that iptables filtering can be configured
          - Check that iptables routing can be configured

        """
        # Naming scheme [resource][id]_[namespace id]
        veth1_1 = 'veth1_1'
        veth1_2 = 'veth1_2'
        address1_1 = '192.168.0.1'
        address1_2 = '192.168.0.2'
        with add_namespaces() as (ns1, ns2):
            # Check that inter-namespace connectivity can be established
            add_veth_pair(ns1, ns2, veth1_1, veth1_2, address1_1, address1_2)
            e('%(ns1)s ip link list')
            e('%(ns1)s ip link show %(veth1_1)s')
            e('%(ns1)s arping -A -U -I %(veth1_1)s '
              '-c 1 %(address1_1)s')
            e('%(ns2)s route add default gw %(address1_1)s')
            e('%(ns2)s ping -c 1 -w 1 %(address1_1)s')
            e('ping -c 1 -w 1 %(address1_1)s', prefix='', return_code=1,
              error_msg='Namespace isolation not supported!')

            # Check that iptables filtering and save/restore can be performed
            try:
                iptables_filename = os.path.join(
                    tempfile.gettempdir(),
                    'iptables-%s' % str(uuid.uuid4()))
                e('%%(ns1)s iptables-save > %s' % iptables_filename)
                e('%(ns1)s iptables -A INPUT -p icmp --icmp-type 8 -j DROP')
                e('%(ns2)s ping -c 1 -w 1 %(address1_1)s', return_code=1)
                e('%%(ns1)s iptables-restore < %s' % iptables_filename)
                e('%(ns2)s ping -c 1 -w 1 %(address1_1)s')
            finally:
                if os.path.exists(iptables_filename):
                    os.unlink(iptables_filename)

            # Create another namespace (ns3) that is connected to ns1
            # via a different subnet, so that traffic between ns3 and
            # ns2 will have to be routed by ns1:
            #
            #  ns2 <- 192.168.0.0/24 -> ns1 <- 192.168.1.0/24 -> ns3
            #
            with add_namespace() as ns3:
                veth2_1 = 'veth2_1'
                veth2_3 = 'veth2_3'
                address2_1 = '192.168.1.1'
                address2_3 = '192.168.1.2'
                add_veth_pair(ns1, ns3, veth2_1, veth2_3,
                              address2_1, address2_3)
                e('%(ns1)s sysctl -w net.ipv4.ip_forward=1')
                e('%(ns1)s iptables -t nat -A POSTROUTING -o %(veth2_1)s -j '
                  'MASQUERADE')
                e('%(ns1)s iptables -A FORWARD -i %(veth2_1)s -o %(veth1_1)s '
                  '-m state --state RELATED,ESTABLISHED -j ACCEPT')
                e('%(ns1)s iptables -A FORWARD -i %(veth1_1)s -o %(veth2_1)s '
                  '-j ACCEPT')
                e('%(ns2)s ping -c 1 -w 1 %(address2_3)s')

            # Check that links can be torn down
            e('%(ns1)s ip -4 addr del %(address1_1)s/24 '
              'dev %(veth1_1)s')
            e('%(ns1)s ip link delete %(veth1_1)s')

    def test_domain_socket_access(self):
        """Check that a domain socket can be accessed regardless of namespace.

        Neutron extends nova' metadata service - which identifies VM's
        by their ip addresses - to configurations with overlapping
        ips.  Support is provided by:

          - a proxy in each namespace (neutron-ns-metadata-proxy)

            - the proxy can uniquely identify a given VM by its ip
              address in the context of the router or network of the
              namespace.

          - a metadata agent (neutron-metadata-agent) that forwards
            requests from the namespace proxies to nova's metadata
            service.

        Communication between the proxies and the agent is over a unix
        domain socket.  It is necessary that access to a domain socket
        not be restricted by namespace, or such communication will not
        be possible.

        """
        try:
            execute('which nc')
        except Exception:
            self.fail("The 'nc' command is not available - please install it.")

        sock_filename = os.path.join(tempfile.gettempdir(),
                                     'testsock-%s' % str(uuid.uuid4()))
        server = None
        try:
            # Create a server in the root namespace attached to a domain socket
            server = e('nc -lU %(sock_filename)s', sudo=False, prefix='',
                       block=False)
            # Attempt to connect to the domain socket from within a namespace
            with add_namespace() as ns:
                e('%(ns)s nc -U %(sock_filename)s', input='magic',
                  error_msg='Unable to communicate between namespaces via '
                            'domain sockets.')
        finally:
            if server:
                server.kill()
            if os.path.exists(sock_filename):
                os.unlink(sock_filename)


if __name__ == '__main__':
    unittest.main()
