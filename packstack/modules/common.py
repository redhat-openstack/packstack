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

from ..installer import utils


def filtered_hosts(config, exclude=True, dbhost=True):
    """
    Returns list of hosts which need installation taking into account
    CONFIG_MARIADB_INSTALL if parameter dbhost is True and EXCLUDE_SERVERS
    if parameter exclude is True.
    """
    exclset = set([i.strip()
                   for i in config.get('EXCLUDE_SERVERS', '').split(',')
                   if i.strip()])
    result = set()
    dbinst = config.get('CONFIG_MARIADB_INSTALL') == 'y'
    vcenter = config.get('CONFIG_VMWARE_BACKEND') == 'y'
    for hosttype, hostname in utils.host_iter(config):
        # if dbhost is being taken into account and we are not installing
        # MariaDB then we should omit the MariaDB host
        if dbhost and not dbinst and hosttype == 'CONFIG_MARIADB_HOST':
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
    # with them when checking all-in-one. MariaDB host should however be
    # omitted if we are not installing MariaDB.
    return len(filtered_hosts(config, exclude=False, dbhost=True)) == 1
