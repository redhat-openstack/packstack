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

"""
Contains all core validation functions.
"""

import logging
import os
import re
import socket

from . import utils

from .exceptions import ParamValidationError


__all__ = ('ParamValidationError', 'validate_integer', 'validate_float',
           'validate_regexp', 'validate_port', 'validate_not_empty',
           'validate_options', 'validate_multi_options', 'validate_ip',
           'validate_multi_ip', 'validate_file', 'validate_ping',
           'validate_multi_ping', 'validate_ssh', 'validate_multi_ssh',
           'validate_sshkey', 'validate_ldap_url', 'validate_ldap_dn',
           'validate_export', 'validate_multi_export',
           'validate_writeable_directory')


def validate_integer(param, options=None):
    """
    Raises ParamValidationError if given param is not integer.
    """
    if not param:
        return
    options = options or []
    try:
        int(param)
    except ValueError:
        logging.debug('validate_integer(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given value is not an integer: %s'
        raise ParamValidationError(msg % param)


def validate_float(param, options=None):
    """
    Raises ParamValidationError if given param is not a float.
    """
    if not param:
        return
    options = options or []
    try:
        float(param)
    except ValueError:
        logging.debug('validate_float(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given value is not a float: %s'
        raise ParamValidationError(msg % param)


def validate_regexp(param, options=None):
    """
    Raises ParamValidationError if given param doesn't match at least
    one of regular expressions given in options.
    """
    if not param:
        return
    options = options or []
    for regex in options:
        if re.search(regex, param):
            break
    else:
        logging.debug('validate_regexp(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given value does not match required regular expression: %s'
        raise ParamValidationError(msg % param)


def validate_multi_regexp(param, options=None):
    """
    Raises ParamValidationError if any of the comma separated values given
    in param doesn't match one of the regular expressions given in options.
    """
    options = options or []
    for i in param.split(','):
        validate_regexp(i.strip(), options=options)


def validate_port(param, options=None):
    """
    Raises ParamValidationError if given param is not a decimal number
    in range (0, 65535).
    """
    if not param:
        return
    options = options or []
    validate_integer(param, options)
    port = int(param)
    if not (port >= 0 and port < 65535):
        logging.debug('validate_port(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given value is outside the range of (0, 65535): %s'
        raise ParamValidationError(msg % param)


def validate_not_empty(param, options=None):
    """
    Raises ParamValidationError if given param is empty.
    """
    options = options or []
    if not param and param is not False:
        logging.debug('validate_not_empty(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given value is not allowed: %s'
        raise ParamValidationError(msg % param)


def validate_options(param, options=None):
    """
    Raises ParamValidationError if given param is not member of options.
    """
    if not param:
        return

    options = options or []
    validate_not_empty(param, options)
    if param not in options:
        logging.debug('validate_options(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given value is not member of allowed values %s: %s'
        raise ParamValidationError(msg % (options, param))


def validate_multi_options(param, options=None):
    """
    Validates if comma separated values given in params are members
    of options.
    """
    if not param:
        return
    options = options or []
    for i in param.split(','):
        validate_options(i.strip(), options=options)


def validate_ip(param, options=None):
    """
    Raises ParamValidationError if given parameter value is not in IPv4
    or IPv6 address.
    """
    if not param:
        return
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(family, param)
            return family
        except socket.error:
            continue
    else:
        logging.debug('validate_ip(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given host is not in IP address format: %s'
        raise ParamValidationError(msg % param)


def validate_multi_ip(param, options=None):
    """
    Raises ParamValidationError if comma separated IP addresses given
    parameter value are in IPv4 or IPv6 aformat.
    """
    for host in param.split(','):
        host = host.split('/', 1)[0]
        validate_ip(host.strip(), options)


def validate_file(param, options=None):
    """
    Raises ParamValidationError if provided file in param does not exist.
    """
    if not param:
        return

    options = options or []
    if not os.path.isfile(param):
        logging.debug('validate_file(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given file does not exist: %s'
        raise ParamValidationError(msg % param)


def validate_writeable_directory(param, options=None):
    """
    Raises ParamValidationError if provided directory does not exist or
    is not writeable.
    """
    if not param:
        return

    options = options or []
    path = os.path.expanduser(param)
    if not ((os.path.isdir(path) and os.access(path, os.W_OK)) or
            os.access(
            os.path.normpath(os.path.join(path, os.pardir)), os.W_OK)):
        logging.debug('validate_writeable_directory(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given directory does not exist or is not writeable: %s'
        raise ParamValidationError(msg % param)


def validate_ping(param, options=None):
    """
    Raises ParamValidationError if provided host does not answer to ICMP
    echo request.
    """
    if not param:
        return
    options = options or []
    rc, out = utils.execute(['/bin/ping', '-c', '1', str(param)],
                            can_fail=False)
    if rc != 0:
        logging.debug('validate_ping(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given host is unreachable: %s'
        raise ParamValidationError(msg % param)


def validate_multi_ping(param, options=None):
    """
    Raises ParamValidationError if comma separated host given in param
    do not answer to ICMP echo request.
    """
    options = options or []
    for host in param.split(","):
        validate_ping(host.strip())


_tested_ports = []


def touch_port(host, port):
    """
    Check that provided host is listening on provided port.
    """
    key = "%s:%d" % (host, port)
    if key in _tested_ports:
        return
    sock = socket.create_connection((host, port))
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    _tested_ports.append(key)


def validate_ssh(param, options=None):
    """
    Raises ParamValidationError if provided host does not listen
    on port 22.
    """
    if not param:
        return
    options = options or []
    try:
        touch_port(param.strip(), 22)
    except socket.error:
        logging.debug('validate_ssh(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given host does not listen on port 22: %s'
        raise ParamValidationError(msg % param)


def validate_multi_ssh(param, options=None):
    """
    Raises ParamValidationError if comma separated host provided
    in param do not listen on port 22.
    """
    options = options or []
    for host in param.split(","):
        validate_ssh(host)


def validate_sshkey(param, options=None):
    """
    Raises ParamValidationError if provided sshkey file is not public key.
    """
    if not param:
        return
    with open(param) as sshkey:
        line = sshkey.readline()
    msg = None
    if not re.search('ssh-|ecdsa', line):
        msg = ('Invalid content header in %s, Public SSH key is required.'
               % param)
    if re.search('BEGIN [RD]SA PRIVATE KEY', line):
        msg = 'Public SSH key is required. You passed private key.'
    if msg:
        raise ParamValidationError(msg)


def validate_ldap_url(param, options=None):
    """
    Raises ParamValidationError if provided param is not a valid LDAP URL
    """
    if not param:
        return
    try:
        import ldapurl
    except ImportError:
        msg = (
            'The python ldap package is required to use this functionality.'
        )
        raise ParamValidationError(msg)

    try:
        ldapurl.LDAPUrl(param)
    except ValueError as ve:
        msg = ('The given string [%s] is not a valid LDAP URL: %s' %
               (param, ve))
        raise ParamValidationError(msg)


def validate_ldap_dn(param, options=None):
    """
    Raises ParamValidationError if provided param is not a valid LDAP DN
    """
    if not param:
        return
    try:
        import ldap
        import ldap.dn
    except ImportError:
        msg = (
            'The python ldap package is required to use this functionality.'
        )
        raise ParamValidationError(msg)

    try:
        ldap.dn.str2dn(param)
    except ldap.DECODING_ERROR as de:
        msg = ('The given string [%s] is not a valid LDAP DN: %s' %
               (param, de))
        raise ParamValidationError(msg)


def validate_export(param, options=None):
    """
    Raises ParamValidationError if the nfs export is not valid.
    """
    msg = ('The nfs export [%s] is not a valid export - use squares around ipv6 addresses -.' %
           param)
    try:
        [ip, export] = param.split(':/')
    except ValueError:
        raise ParamValidationError(msg)
    get_squares = re.search(r'\[([^]]+)\]', ip)
    ip_to_test = ip
    if get_squares:
        # this should be a valid ipv6 address.
        ip_to_test = get_squares.group(1)
        if not utils.network.is_ipv6(ip_to_test):
            raise ParamValidationError(msg)
    else:
        # this should be an ipv4. Cannot have ipv6 without square braquet
        # notation here, as the mount will fail.
        if not utils.network.is_ipv4(ip):
            raise ParamValidationError(msg)
    validate_ip(ip_to_test, options)
    if not export:
        raise ParamValidationError(msg)


def validate_multi_export(param, options=None):
    """
    Raises ParamValidationError if comma separated nfs export given
    in param is not valid
    """
    for export in param.split(","):
        validate_export(export)


def validate_neutron(param, options=None):
    """
    Raises ParamValidationError if neutron is not enabled.
    This is intended to make user aware nova-network has been removed
    in ocata cycle.
    """
    validate_options(param, options=options)
    if param != 'y':
        msg = ('Nova network support has been removed in Ocata. Neutron service must be enabled')
        raise ParamValidationError(msg)
