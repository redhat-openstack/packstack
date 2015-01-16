# -*- coding: utf-8 -*-

import netaddr
import os
import uuid

from .utils import ScriptRunner, force_ip
from .exceptions import ParamProcessingError, NetworkError


__all__ = ('ParamProcessingError', 'process_cidr', 'process_host',
           'process_ssh_key')


def process_cidr(param, param_name, config=None):
    """
    Corrects given CIDR if necessary.
    """
    if '/' not in param:
        # we need to skip this if single IP address has been given
        return param
    try:
        return str(netaddr.IPNetwork(param).cidr)
    except Exception as ex:
        raise ParamProcessingError(str(ex))


def process_host(param, param_name, config=None):
    """
    Tries to change given parameter to IP address, if it is in hostname
    format
    """
    try:
        return force_ip(param, allow_localhost=True)
    except NetworkError as ex:
        raise ParamProcessingError(str(ex))


def process_ssh_key(param, param_name, config=None):
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


def process_add_quotes_around_values(param, param_name, config=None):
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


def process_password(param, param_name, config=None):
    """
    Process passwords, checking the following:
    1- If there is a user-entered password, use it
    2- Otherwise, check for a global default password, and use it if available
    3- As a last resort, generate a random password
    """
    if not hasattr(process_password, "pw_dict"):
        process_password.pw_dict = {}

    if param == "PW_PLACEHOLDER":
        if config["CONFIG_DEFAULT_PASSWORD"] != "":
            param = config["CONFIG_DEFAULT_PASSWORD"]
        else:
            # We need to make sure we store the random password we provide
            # and return it once we are asked for it again
            if param_name.endswith("_CONFIRMED"):
                unconfirmed_param = param_name[:-10]
                if unconfirmed_param in process_password.pw_dict:
                    param = process_password.pw_dict[unconfirmed_param]
                else:
                    param = uuid.uuid4().hex[:16]
                    process_password.pw_dict[unconfirmed_param] = param
            elif param_name not in process_password.pw_dict:
                param = uuid.uuid4().hex[:16]
                process_password.pw_dict[param_name] = param
            else:
                param = process_password.pw_dict[param_name]
    return param
