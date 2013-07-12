# -*- coding: utf-8 -*-

from .ospluginutils import gethostlist


def is_all_in_one(config):
    """
    Returns True if packstack is running allinone setup, otherwise
    returns False.
    """
    return len(gethostlist(config)) == 1
