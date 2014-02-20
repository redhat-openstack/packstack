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
    vcenter = config.get('CONFIG_VMWARE_BACKEND') == 'y'
    for hosttype, hostname in utils.host_iter(config):
        # if dbhost is being taken into account and we are not installing MySQL
        # then we should omit the MySQL host
        if dbhost and not dbinst and hosttype == 'CONFIG_MYSQL_HOST':
            continue
        if vcenter and hosttype == 'CONFIG_VCENTER_HOST':
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
    # Even if some host have been excluded from installation, we must count
    # with them when checking all-in-one. MySQL host should however be omitted
    # if we are not installing MySQL
    return len(filtered_hosts(config, exclude=False, dbhost=True)) == 1
