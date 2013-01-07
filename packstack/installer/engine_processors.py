# -*- coding: utf-8 -*-

from .common_utils import forceIP
from .exceptions import ParamProcessingError, NetworkError


__all__ = ('ParamProcessingError', 'processHost')



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
