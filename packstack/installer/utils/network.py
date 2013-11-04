# -*- coding: utf-8 -*-

import re
import socket

from ..exceptions import NetworkError
from .shell import execute, ScriptRunner


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


def host2ip(hostname, allow_localhost=False):
    """
    Converts given hostname to IP address. Raises NetworkError
    if conversion failed.
    """
    try:
        ip_list = socket.gethostbyaddr(hostname)[2]
        if allow_localhost:
            return ip_list[0]
        else:
            local_ips = ('127.0.0.1', '::1')
            for ip in ip_list:
                if ip not in local_ips:
                    break
            else:
                raise NameError()
            return ip
    except NameError:
        # given hostname is localhost, return appropriate IP address
        return get_localhost_ip()
    except socket.error:
        raise NetworkError('Unknown hostname %s.' % hostname)
    except Exception, ex:
        raise NetworkError('Unknown error appeared: %s' % repr(ex))


def force_ip(host, allow_localhost=False):
    host = host.strip()
    ipv4_regex = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    ipv6_regex = re.compile('[abcdef\d\:]+')
    if not ipv4_regex.match(host) or not ipv6_regex.match(host):
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
