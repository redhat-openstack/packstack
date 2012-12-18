# -*- coding: utf-8 -*-

from .common_utils import UtilsNetworkError, forceIP



__all__ = ('ParamProcessingError', 'processHost')


class ParamProcessingError(Exception):
    pass


def processHost(param, process_args=None):
    """
    Given parameter is a hostname, try to change it to IP address
    """
    localhost = process_args and \
                process_args.get('allow_localhost', False)
    try:
        return forceIP(param, allow_localhost=localhost)
    except UtilsNetworkError, ex:
        raise ParamProcessingError(str(ex))
