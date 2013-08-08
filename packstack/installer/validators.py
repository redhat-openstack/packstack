# -*- coding: utf-8 -*-

"""
Contains all core validation functions.
"""

import os
import re
import socket
import logging
import tempfile
import traceback

import basedefs
from . import utils

from .setup_controller import Controller
from .exceptions import ParamValidationError


__all__ = ('ParamValidationError', 'validate_integer', 'validate_float',
           'validate_regexp', 'validate_port', 'validate_not_empty',
           'validate_options', 'validate_ip', 'validate_multi_ip',
           'validate_file', 'validate_ping', 'validate_ssh',
           'validate_multi_ssh')


def validate_integer(param, options=None):
    """
    Raises ParamValidationError if given param is not integer.
    """
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
    options = options or []

    # TO-DO: to be more flexible, remove this and exit in case param is empty
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
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(family, param)
            break
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
        host, device = host.split('/', 1)
        validate_ip(host.strip(), options)


def validate_file(param, options=None):
    """
    Raises ParamValidationError if provided file in param does not exist.
    """
    options = options or []
    # TO-DO: to be more flexible, remove this and exit in case param is empty
    validate_not_empty(param)

    if not os.path.isfile(param):
        logging.debug('validate_file(%s, options=%s) failed.' %
                      (param, options))
        msg = 'Given file does not exist: %s'
        raise ParamValidationError(msg % param)


def validate_ping(param, options=None):
    """
    Raises ParamValidationError if provided host does not answer to ICMP
    echo request.
    """
    options = options or []
    # TO-DO: to be more flexible, remove this and exit in case param is empty
    validate_not_empty(param)

    rc, out = utils.execute(['/bin/ping', '-c', '1', str(param)],
                            can_fail=True)
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
    # TO-DO: to be more flexible, remove this and exit in case param is empty
    validate_not_empty(param)
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    _tested_ports.append(key)


def validate_ssh(param, options=None):
    """
    Raises ParamValidationError if provided host does not listen
    on port 22.
    """
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
