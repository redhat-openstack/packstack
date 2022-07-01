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

import grp
import os
import pwd


def host_iter(config):
    for key, value in config.items():
        if key.endswith("_HOST"):
            host = value.split('/')[0]
            if host:
                yield key, host
        if key.endswith("_HOSTS"):
            for i in value.split(","):
                host = i.strip().split('/')[0]
                if host:
                    yield key, host


def hosts(config):
    result = set()
    for key, host in host_iter(config):
        result.add(host)
    return result


def get_current_user():
    try:
        user = pwd.getpwnam(os.getlogin())
        uid, gid = user.pw_uid, user.pw_gid
    except OSError:
        # in case program is run by a script
        uid, gid = os.getuid(), os.getgid()
    return uid, gid


def get_current_username():
    uid, gid = get_current_user()
    user = pwd.getpwuid(uid).pw_name
    group = grp.getgrgid(gid).gr_name
    return user, group


def split_hosts(hosts_string):
    hosts = set()
    for host in hosts_string.split(','):
        shost = host.strip()
        if shost:
            hosts.add(shost)
    return hosts
