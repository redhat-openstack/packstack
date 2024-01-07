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

import netaddr
import os
import uuid

from .utils import force_ip
from .utils import ScriptRunner
from .exceptions import NetworkError
from .exceptions import ParamProcessingError


__all__ = ('ParamProcessingError', 'process_cidr', 'process_host',
           'process_ssh_key', 'process_add_quotes_around_values',
           'process_password', 'process_string_nofloat', 'process_bool')


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


def process_heat(param, param_name, config=None):
    return param


def process_string_nofloat(param, param_name, config=None):
    """
    Process a string, making sure it is *not* convertible into a float
    If it is, change it into a random 16 char string, and check again
    """
    while True:
        try:
            float(param)
        except ValueError:
            return param
        else:
            param = uuid.uuid4().hex[:16]


def process_bool(param, param_name, config=None):
    """Converts param to appropriate boolean representation.

    Retunrs True if answer == y|yes|true, False if answer == n|no|false.
    """
    if param.lower() in ('y', 'yes', 'true'):
        return True
    elif param.lower() in ('n', 'no', 'false'):
        return False


# Define silent processors
for proc_func in (process_bool, process_add_quotes_around_values):
    proc_func.silent = True
