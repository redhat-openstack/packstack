# -*- coding: utf-8 -*-

import os

from .utils import ScriptRunner, force_ip
from .exceptions import ParamProcessingError, NetworkError


__all__ = ('ParamProcessingError', 'process_host', 'process_ssh_key')


def process_host(param, process_args=None):
    """
    Tries to change given parameter to IP address, if it is in hostname
    format
    """
    localhost = process_args and \
                process_args.get('allow_localhost', False)
    try:
        return force_ip(param, allow_localhost=localhost)
    except NetworkError, ex:
        raise ParamProcessingError(str(ex))


def process_ssh_key(param, process_args=None):
    """
    Generates SSH key if given key in param doesn't exist. In case param
    is an empty string it generates default SSH key ($HOME/.ssh/id_rsa).
    """
    def create_key(path):
        # make path absolute
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        # create new ssh key
        local = ScriptRunner()
        local.append('ssh-keygen -f "%s" -N ""' % path)
        local.execute()

    if not param:
        key_file = '%s/.ssh/id_rsa' % os.environ["HOME"]
        param = '%s.pub' % key_file
        if not os.path.isfile(param):
            create_key(key_file)
    elif not os.path.isfile(param):
        key_file = param.endswith('.pub') and param[:-4] or param
        param = param.endswith('.pub') and param or ('%s.pub' % param)
        create_key(key_file)
    return param


def process_add_quotes_around_values(param, process_args=None):
    """
    Add a single quote character around each element of a comma
    separated list of values
    """
    params_list = param.split(',')
    for index, elem in enumerate(params_list):
        if not elem.startswith("'"):
            elem = "'" + elem
        if not elem.endswith("'"):
            elem = elem + "'"
        params_list[index] = elem
    param = ','.join(params_list)
    return param
