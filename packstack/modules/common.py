# -*- coding: utf-8 -*-

from ..installer import utils


def filtered_hosts(config, exclude=True, dbhost=True):
    """
    Returns list of hosts which need installation taking into account
    CONFIG_MYSQL_INSTAL if parameter dbhost is True and EXCLUDE_SERVERS
    if parameter exclude is True.
    """
    exclset = set([i.strip()
                   for i in config.get('EXCLUDE_SERVERS', '').split(',')
                   if i.strip()])
    result = set()
    dbinst = config.get('CONFIG_MYSQL_INSTALL') == 'y'
    for hosttype, hostname in utils.host_iter(config):
        if dbhost and not dbinst and hosttype == 'CONFIG_MYSQL_HOST':
            continue
        result.add(hostname)
    if exclude:
        result = result - exclset
    return result


def is_all_in_one(config):
    """
    Returns True if packstack is running allinone setup, otherwise
    returns False.
    """
    return len(filtered_hosts(config, exclude=False)) == 1
