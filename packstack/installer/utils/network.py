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

netaddr_available = True
try:
    import netaddr
except ImportError:
    netaddr_available = False

import re
import socket
import logging
from ..exceptions import NetworkError
from .shell import execute
from .shell import ScriptRunner


def get_localhost_ip():
    """
    Returns IP address of localhost.
    """
    # TO-DO: Will probably need to find better way to find out localhost
    #        address.

    # find nameservers
    ns_regex = re.compile('nameserver\s*(?P<ns_ip>[\d\.\:]+)')
    rc, resolv = execute('cat /etc/resolv.conf | grep nameserver',
                         can_fail=False, use_shell=True, log=False)
    nsrvs = []
    for line in resolv.split('\n'):
        match = ns_regex.match(line.strip())
        if match:
            nsrvs.append(match.group('ns_ip'))

    # try to connect to nameservers and return own IP address
    nsrvs.append('8.8.8.8')  # default to google dns
    for i in nsrvs:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((i, 0))
            loc_ip = s.getsockname()[0]
        except socket.error:
            continue
        else:
            return loc_ip
    raise NetworkError('Local IP address discovery failed. Please set '
                       'nameserver correctly.')


_host_cache = {}


def host2ip(hostname, allow_localhost=False):
    """
    Converts given hostname to IP address. Raises NetworkError
    if conversion failed.
    """
    key = '{}:{}'.format(hostname, allow_localhost)
    if key in _host_cache:
        return _host_cache[key]
    try:
        ip_list = list(sockets[4][0] for sockets in
                       socket.getaddrinfo(hostname, 22, 0, 0, socket.IPPROTO_TCP))

        if allow_localhost:
            ip = ip_list[0]
        else:
            routable = [ip for ip in ip_list if ip not in ('127.0.0.1', '::1')]
            if not routable:
                raise NameError("Host %s is not routable, please fix"
                                "your /etc/hosts", host)
            if len(routable) > 1:
                logging.warning("Multiple IPs for host detected!")
            ip = routable[0]

        _host_cache[key] = ip
        return ip
    except NameError:
        # given hostname is localhost, return appropriate IP address
        return get_localhost_ip()
    except socket.error:
        raise NetworkError('Unknown hostname %s.' % hostname)
    except Exception as ex:
        raise NetworkError('Unknown error appeared: %s' % repr(ex))


def is_ipv6(host):
    if not netaddr_available:
        raise ImportError(
            "netaddr module unavailable, install with pip install netaddr"
        )
    host = host.strip()
    try:
        return netaddr.IPAddress(host.strip('[]')).version == 6
    except netaddr.core.AddrFormatError:
        # Most probably a hostname
        return False


def is_ipv4(host):
    if not netaddr_available:
        raise ImportError(
            "netaddr module unavailable, install with pip install netaddr"
        )
    host = host.strip()
    try:
        return netaddr.IPAddress(host).version == 4
    except netaddr.core.AddrFormatError:
        # Most probably a hostname
        return False


def force_ip(host, allow_localhost=False):
    if not(is_ipv6(host) or is_ipv4(host)):
        host = host2ip(host, allow_localhost=allow_localhost)
    return host


def device_from_ip(ip):
    server = ScriptRunner()
    server.append("DEVICE=($(ip -o address show to %s | cut -f 2 -d ' '))"
                  % ip)
    # Ensure that the IP is only assigned to one interface
    server.append("if [ ! -z ${DISPLAY[1]} ]; then false; fi")
    # Test device, raises an exception if it doesn't exist
    server.append("ip link show \"$DEVICE\" > /dev/null")
    server.append("echo $DEVICE")
    rv, stdout = server.execute()
    return stdout.strip()
