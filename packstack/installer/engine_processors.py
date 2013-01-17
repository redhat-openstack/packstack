# -*- coding: utf-8 -*-

import os

from .common_utils import ScriptRunner, forceIP
from .exceptions import ParamProcessingError, NetworkError


__all__ = ('ParamProcessingError', 'processHost', 'processSSHKey')



def processHost(param, process_args=None):
    """
    Given parameter is a hostname, try to change it to IP address
    """
    localhost = process_args and \
                process_args.get('allow_localhost', False)
    try:
        return forceIP(param, allow_localhost=localhost)
    except NetworkError, ex:
        raise ParamProcessingError(str(ex))

def processSSHKey(param, process_args=None):
    """
    Generates SSH key if given key in param doesn't exist. In case param
    is an empty string it generates default SSH key ($HOME/.ssh/id_rsa).
    """
    def create_key(path):
        local = ScriptRunner()
        # create new ssh key
        local.append('ssh-keygen -f %s -N ""' % path)
        local.execute()

    if not param:
        key_file = '%s/.ssh/id_rsa' % os.environ["HOME"]
        param = '%s.pub' % key_file
        if not os.path.isfile(param):
            create_key(key_file)
    elif not os.path.isfile(param):
        key_file = param.endswith('.pub') and param[:-4] or param
        create_key(key_file)
    return param
