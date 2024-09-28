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

import logging
import netifaces
import socket

from ..exceptions import NetworkError
from .shell import ScriptRunner

netaddr_available = True
try:
    import netaddr
except ImportError:
    netaddr_available = False


def get_localhost_ip():
    """
    Returns IP address of localhost.
    """
    # Try to get the IPv4 or IPv6 default gateway, then open a socket
    # to discover our local IP
    gw = None
    for protocol in (socket.AF_INET, socket.AF_INET6):
        try:
            gw = netifaces.gateways()['default'][protocol][0]
            if protocol == socket.AF_INET6:
                gw = gw + '%' + netifaces.gateways()['default'][protocol][1]
            discovered_protocol = protocol
            break
        except KeyError:    # No default gw for this protocol
            continue
    else:
        raise NetworkError('Local IP address discovery failed. Please set '
                           'a default gateway for your system.')

    address = socket.getaddrinfo(gw, 0, discovered_protocol,
                                 socket.SOCK_DGRAM)[0]
    s = socket.socket(discovered_protocol, socket.SOCK_DGRAM)
    s.connect(address[4])
    # Remove chars after %. Does nothing on IPv4, removes scope id in IPv6
    loc_ip = s.getsockname()[0].split('%')[0]

    return loc_ip


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
    if not (is_ipv6(host) or is_ipv4(host)):
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
